from flask import Flask, request, jsonify
from google import genai
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
API_KEY = ""
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})
client = None
current_model = None
lang = None
interview_type = None
domain = None
duration = 0
interview_start = False
current_time = None
current_hour = None
previous_q = ""
previous_res = ""
language_options = {
    "en-US": "English (US)",
    "bn-IN": "Bengali",
    "es-ES": "Spanish",
    "fr-FR": "French",
    "de-DE": "German",
    "hi-IN": "Hindi",
    "zh-CN": "Chinese",
    "ja-JP": "Japanese",
    "ru-RU": "Russian",
    "ar-SA": "Arabic",
    "pt-BR": "Portuguese"
}

interview_types= {
    "tech": "technical",
    "hr": "Behavioral(HR)"
}

domains={
    "ml": "Machine Learning",
    "ds": "Data Science",
    "bd": "Backend Development",
    "fd": "Frontend Development",
    "mlops": "MLOps",
    "dops": "DevOps",
    "mapp": "Mobile Application Development",
    "": "Behavioral"
}

def time_of_day(hour):
    if 4 <= hour < 12:
        return "Morning"
    elif 12 <= hour <= 17:
        return "Afternoon"
    else:
        return "Evening"
    
@app.route('/chat', methods=["POST"])
def reply():
    global previous_q, previous_res, interview_start
    data = request.get_json()
    user_response = data.get("prompt", "").strip()

    previous_res = user_response
    if(interview_start):
        messages = f'''
        You are a {interview_types[interview_type]} interviewer in the {domains[domain]} domain.
        Your **ABSOLUTE AND SOLE LANGUAGE OF COMMUNICATION IS {language_options[lang]}**.
        You must **under no circumstances** use any words, phrases, or sentences from English or any other language.
        **Every single output must be 100% in {language_options[lang]}. No exceptions.**

        This is the start of the interview.
        1. First, greet the candidate based on the {time_of_day(current_hour)}. Ensure this greeting is **entirely in {language_options[lang]}**.
        2. Then, ask the first question from the {domains[domain]} domain. This question must also be **completely in {language_options[lang]}**.

        ### Strict Language Enforcement Rules:
        * **Primary Language:** STRICTLY {language_options[lang]} only.
        * **Forbidden:** DO NOT use English words, phrases, or concepts translated into English phrasing.
        * **Output Purity:** Ensure the entire response, from start to finish, contains ZERO words from any other language.
        * **Role:** You are a {language_options[lang]} interviewer. Speak as such.
        '''
        interview_start = False
    else:
        messages = f'''
           You are a {interview_types[interview_type]} interviewer in the {domains[domain]} domain.
            Your **ABSOLUTE AND SOLE LANGUAGE OF COMMUNICATION IS {language_options[lang]}**.
            You must **under no circumstances** use any words, phrases, or sentences from English or any other language.
            **Every single output must be 100% in {language_options[lang]}. No exceptions.**

            You will ask follow-up questions, evaluate answers, and behave like a professional interviewer.

            ***Previous Question Asked***: {previous_q}
            ***Candidate's Last Response***: {previous_res}

            ### Strict Interview Guidelines:
            * **Language Constraint:** STRICTLY {language_options[lang]} only. DO NOT use English or any other language. All communication must be in {language_options[lang]}.
            * **Response Handling & Questioning Flow:**
                * **If the Candidate's Last Response is empty or extremely brief** (e.g., just "ok", "yes", "no", a single word, or merely acknowledgements):
                    * DO NOT provide feedback for this response.
                    * Immediately ask the next logical question to advance the interview in the {domains[domain]} domain, without acknowledging the brevity of the previous answer.
                * **If the Candidate's Last Response is NOT empty and contains a substantial answer:**
                    1.  **Evaluate:** First, provide concise, constructive feedback on the "Candidate's Last Response". Your feedback must be professional, supportive, and focus on clarity, completeness, relevance, and conciseness, without assigning a direct score. Your feedback must be entirely in {language_options[lang]}.
                    2.  **Follow-up Question:** Immediately after your feedback, ask **ONE** follow-up question. This question must be directly related to the "Candidate's Last Response" or the "Previous Question Asked", and it should logically progress the interview in the {domains[domain]} domain.
            * **Single Question Rule:** Always ask **only one** question at a time. Do not ask multiple questions in a single turn. 
    '''
    response = client.models.generate_content(model="gemini-2.5-flash", contents=messages)
    previous_q = response.text
    return jsonify({"response": response.text})

@app.route('/info', methods=["POST"])
def process_info():

    global current_model, API_KEY, lang, interview_type, domain, duration, interview_start, current_time, current_hour, client

    data = request.get_json()
    current_model = data.get("model")
    API_KEY = data.get("api")
    lang = data.get("lang")
    interview_type = data.get("type")
    domain = data.get("domain")
    duration = data.get("duration")
    interview_start = True
    current_time = datetime.now()
    current_hour = current_time.hour
    client = genai.Client(api_key=API_KEY)

    print("Model:", current_model)
    print("Lang:", lang)
    print("Interview type:", interview_type)
    print("Domain:", domain)
    print("Duration:", duration)
    print("Interview starts at:", current_time.strftime("%H:%M"))

    return jsonify({'response': "OK"})

@app.route('/feedback', methods=["POST"])
def giveFeedback():
    global previous_q, previous_res
    data = request.get_json()
    conv_his = data.get("conv_his")
    system_des = f'''
        You are a {interview_types[interview_type]} interviewer in the {domains[domain]} domain.
        Your **ABSOLUTE AND SOLE LANGUAGE OF COMMUNICATION IS {language_options[lang]}**.
        You must **under no circumstances** use any words, phrases, or sentences from English or any other language.
        **Every single output must be 100% in {language_options[lang]}. No exceptions.**

        The interview has concluded. You will now provide a comprehensive final feedback report based on the entire conversation history.

        ***Full Interview Conversation History***:
        {conv_his}

        ### Final Feedback Guidelines:
        * **Language Constraint:** STRICTLY {language_options[lang]} only. DO NOT use English or any other language. All communication must be in {language_options[lang]}.
        * **Content & Structure:**
            * Provide an **overall assessment** of the candidate's performance in the {domains[domain]} domain based on the entire interview.
            * Identify specific **strengths** the candidate demonstrated during the conversation, providing concrete examples where possible.
            * Outline clear **areas for improvement** for the candidate. For each area, provide actionable and specific advice or suggestions on how they can enhance their skills or approach.
            * Conclude with a professional and encouraging closing statement.
            * Organize your feedback into distinct, clearly labeled sections (e.g., using headings or bullet points) in {language_options[lang]} for readability.
        * **Tone:** Maintain a **professional, constructive, and encouraging tone** throughout the feedback. The goal is to help the candidate improve.
        * **Conciseness:** The feedback should be concise yet comprehensive, providing valuable insights without excessive length. Aim for a well-structured summary.
        '''
    feedback = client.models.generate_content(model="gemini-2.5-flash", contents=system_des)
    previous_q = ""
    previous_res = ""
    return jsonify({"response": feedback.text})

if __name__ == "__main__":
    app.run(port=5000)