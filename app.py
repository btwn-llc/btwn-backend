from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import io

app = Flask(__name__)
CORS(app)

parsed_resumes: list = []

@app.route('/submit_resumes', methods=['POST'])
def submit_resumes():
    if 'resumes' not in request.files:
        return jsonify({"error": "No resume files provided"}), 400
    
    resumes = request.files.getlist('resumes')
    global parsed_resumes
    
    for resume in resumes:
        if not resume.filename:
            continue
        if resume.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            parsed_resumes.append(text)
    
    return jsonify({"message": "Resumes submitted successfully"}), 201

@app.route('/get_industries', methods=['GET'])
def get_industries():
    if len(parsed_resumes) == 0:
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
    return jsonify({"message": "Hello, World!"})


if __name__ == '__main__':
    app.debug = True
    app.run()
