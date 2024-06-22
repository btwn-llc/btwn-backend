from flask import Flask, request, jsonify, json
from flask_cors import CORS
import llm
import PyPDF2
import io
import ast

app = Flask(__name__)
CORS(app)


class Session:
    def __init__(self):
        self.parsed_resumes: list = []

sessions: 'dict[str, Session]' = {"default" : Session()} # session_id -> Session


def get_session_id() -> str|None:
    session_id = request.headers.get('session_id')
    return session_id

@app.route('/create_session', methods=['POST'])
def create_session():
    session_id = get_session_id()
    if session_id is None:
        return jsonify({"error" : "No session_id providded"}), 400
    global sessions
    sessions[session_id] = Session()
    print("Session {} created successfully".format(session_id))
    return jsonify({"message": "Session id: {} created successfully".format(session_id)}), 201


@app.route('/submit_resumes', methods=['POST'])
def submit_resumes():
    try:
        print("submit resumes")

        if request.files is None:
            return jsonify({"error": "No files provided"}), 400

        if 'resumes' not in request.files:
            return jsonify({"error": "No resume files provided"}), 400

        session_id: str|None = get_session_id()

        print("session_id: ", session_id)

        if not session_id:
            return jsonify({"error" : "No session_id providded"}), 400
        print("getting session")

        session: Session = sessions.get(session_id) # type: ignore
        print("getting resumes")
        
        resumes = request.files.getlist('resumes')
        
        num_resumes_submitted: int = 0
        for resume in resumes:
            if not resume.filename:
                continue
            if resume.filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                session.parsed_resumes.append(text)
                num_resumes_submitted += 1

        # extract names from each resume
        names: "list[str]" = []
        try:
            for resume in session.parsed_resumes:
                prompt: str = "Extract the name of the owner of the resume. Make sure the name is in right format(first letter capitalized.). Only provide the name and say nothing else. Name: \n" + resume
                extracted_name: str = llm.query_openai(prompt)
                names.append(extracted_name)
                print("Extracted name: ", extracted_name)
        except Exception as e:
            print("Error extracting names: ", str(e))
            return jsonify({"error", "Error extracting names from resume"}), 500
        
        return jsonify({"names": names, "message": "{} resumes submitted successfully".format(num_resumes_submitted)}), 201
    except Exception as e:
        return jsonify({"unknown error": str(e)}), 500

@app.route('/get_industries', methods=['GET'])
def get_industries():

    def parse_llm_response(llm_response: str) -> 'list[str]':
        # delete brackets
        llm_response = llm_response.replace("[","")
        llm_response = llm_response.replace("]","")
        # split by comma
        ret = llm_response.split(",")
        # get rid of whitespaces
        for i in range(len(ret)):
            ret[i] = ret[i].strip()
        return ret

    session_id: str|None = get_session_id()
    
    if not session_id:
        return jsonify({"error" : "No session_id providded"}), 400

    session: Session = sessions.get(session_id) # type: ignore

    if len(session.parsed_resumes) == 0:
        return jsonify({"errors": "No resumes submitted"}), 400

    industries: 'set[str]' = set()

    for resume in session.parsed_resumes:
        prompt: str = f"{resume} \n Above is a text resume of a person, Please extract at most three industries that the person could be a good fit for. \
                return the industries as a parseable string list, with a emoji for each industry, such as [🏥 healthcare, 🍀 environment, 💻 technology]. Only return the bracked list and nothing else.\
                list: ".format(resume=resume)
        llm_response: str = llm.query_openai(prompt)
        llm_resopnse_parsed = parse_llm_response(llm_response)
        industries.update(llm_resopnse_parsed)
        # parse the response in form of [industyr1, industry2, industry3]

    industries_ls: 'list[str]' = list(industries)
    
    return jsonify({"industries": industries_ls}), 200


@app.route('/')
def hello():
    return jsonify({"message": "Hello, Bhada!"})


if __name__ == '__main__':
    app.debug = True
    app.run()
