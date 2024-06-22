from flask import Flask, jsonify, request
import os
import requests
from flask_cors import CORS
import llm
import PyPDF2
import io
import json
from dotenv import load_dotenv
from scrape import scrape_article_content, scrape_youtube_comments
from llm import query_openai
load_dotenv('.env.local')

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
    return jsonify({"message": "bye!"})

@app.route('/search/<query>', methods=['GET'])
def web_search(query):
    headers = {"X-API-Key": os.environ.get('YOU_WEB_SEARCH_API')}
    params = {"query": query, "country": "US", "num_web_results": 10}
    print("headers", headers)
    req = requests.get(
        f"https://api.ydc-index.io/search",
        params=params,
        headers=headers,
    )
    result = req.json()
    return result

@app.route('/top-desires', methods=['POST'])
def top_desires():
    data = request.json

    # Ensure 'industries' is provided in the request and is a list
    if not data or 'industries' not in data or not isinstance(data['industries'], list):
        return jsonify({"error": "Invalid input. Please provide a list of industries."}), 400
    
    industries = data['industries']
    
    # Ensure the list contains at most 3 industries
    if len(industries) > 3:
        return jsonify({"error": "You can provide a maximum of 3 industries."}), 400

    print("chosen industries", industries)
    
    
    # Ensure 'companies' is provided in the request and is a list
    if not data or 'companies' not in data or not isinstance(data['companies'], list):
        return jsonify({"error": "Invalid input. Please provide a list of companies."}), 400
    
    companies = data['companies']
    
    # Ensure the list contains at most 3 industries
    if len(companies) > 10:
        return jsonify({"error": "You can provide a maximum of 10 companies."}), 400

    print("chosen companies", companies)
    all_comments = []
    all_youtube_videos = set()
    for company in companies:
        results = web_search(f"youtube videos for : {company}")
        company_comments = []
        for result in results["hits"]:
            link = result["url"]
            if 'https://www.youtube.com/watch?' in link and len(company_comments) > 5:
                break
            comments = scrape_youtube_comments(link)
            if comments:
                company_comments.append(comments)
                all_youtube_videos.add(link)
        print("company", company, company_comments)
        all_comments.extend(company_comments)

    print("got the results of length: ", len(all_comments))
    prompt = f"These are a collection of youtube comments about these industries {industries}: {all_comments}. I am trying to create a startup; can you consolidate a list of top 10 desires of users that would be good startup ideas based on these comments?"
    print("prompt", prompt)
    result = query_openai(prompt)
    print("top desires results", result)
    my_list = result.split('\n')

    # Remove numbers from each element in the list
    desires = [item.split('. ', 1)[1] if item.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) else item for item in my_list]

    return jsonify({"desires": desires, "sources": list(all_youtube_videos)}) # company and description

    
@app.route('/top-companies', methods=['POST'])
def top_companies():
    data = request.json
    
    # Ensure 'industries' is provided in the request and is a list
    if not data or 'industries' not in data or not isinstance(data['industries'], list):
        return jsonify({"error": "Invalid input. Please provide a list of industries."}), 400
    
    industries = data['industries']
    
    # Ensure the list contains at most 3 industries
    if len(industries) > 3:
        return jsonify({"error": "You can provide a maximum of 3 industries."}), 400

    print("chosen industries", industries)
    
    # Get the top companies for the given industries
    results = web_search(f"top companies in: {', '.join(industries)}")

    print("got the results of length: ", len(results))
    
    # Scrape top 5 links
    top_companies_result = []
    for result in results["hits"]:
        link = result["url"]
        article_result = scrape_article_content(link)
        if article_result:
            top_companies_result.append(article_result)
            print("Successfully retrieved: ", link)
        if len(top_companies_result) >= 5:
            break

    # Filter with OpenAI
    prompt = f"Can you glean the top 10 companies from these results along with a description of them and format it into a list of dictionaries with keys of company_name and company description: {top_companies_result}"
    result = query_openai(prompt)
    result = json.loads(result)
    print("dana's results", result)
    return jsonify({"industries": industries, "top_companies": result}) # company and description


if __name__ == '__main__':
    app.run(debug=True)
    # results = get_ai_snippets_for_query("reasons to smile")
    # print(results)



