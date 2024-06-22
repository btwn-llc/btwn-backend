from flask import Flask, request, jsonify, json
from flask_cors import CORS
import llm
import PyPDF2
import io

app = Flask(__name__)
CORS(app)


class Session:
    def __init__(self):
        self.parsed_resumes: list = []

sessions: 'dict[str, Session]' = {"default" : Session()} # session_id -> Session


def get_session_id() -> str|None:
    data =  request.get_json()
    if data is None:
        return None
    session_id: str|None = data.get('session_id')
    return session_id

@app.route('/create_session', methods=['POST'])
def create_session():
    session_id = get_session_id()
    if session_id is None:
        return jsonify({"error" : "No session_id providded"}), 400
    sessions[session_id] = Session()
    return jsonify({"message": "Session id: {} created successfully".format(session_id)}), 201


@app.route('/submit_resumes', methods=['POST'])
def submit_resumes():
    if 'resumes' not in request.files:
        return jsonify({"error": "No resume files provided"}), 400

    session_id: str|None = get_session_id()
    
    if not session_id:
        return jsonify({"error" : "No session_id providded"}), 400

    session: Session = sessions.get(session_id) # type: ignore
    
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
    for resume in session.parsed_resumes:
        prompt: str = "Extract the name of the owner of the resume: \n" + resume
        extracted_name: str = llm.query_openai(prompt) 
        names.append(extracted_name)
        print("Extracted name: ", extracted_name)
    
    return jsonify({"names": names, "message": "{} resumes submitted successfully".format(num_resumes_submitted)}), 201

@app.route('/get_industries', methods=['GET'])
def get_industries():

    session_id: str|None = get_session_id()
    
    if not session_id:
        return jsonify({"error" : "No session_id providded"}), 400

    session: Session = sessions.get(session_id) # type: ignore

    if len(session.parsed_resumes) == 0:
        return jsonify({"errors": "No resumes submitted"}), 400
    
    industries = [
        "Technology",
        "Healthcare",
        "Finance",
        "Education",
        "Manufacturing",
        "Retail"
    ]
    return jsonify({"industries": industries})

@app.route('/')
def hello():
    return jsonify({"message": "Hello, Bhada!"})


if __name__ == '__main__':
    app.debug = True
    app.run()
