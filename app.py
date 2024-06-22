from flask import Flask, jsonify, request
import os
import requests
from flask_cors import CORS
import llm
import PyPDF2
import io
import json
from dotenv import load_dotenv
from scrape import scrape_article_content, scrape_youtube_comments, youtube_search
from llm import query_openai
import time
load_dotenv('.env.local')
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
    return jsonify({"message": "bye!"})

@app.route('/search/<query>', methods=['GET'])
def web_search(query):
    headers = {"X-API-Key": os.environ.get('YOU_WEB_SEARCH_API')}
    params = {"query": query, "country": "US", "num_web_results": 20}
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
    start_time = time.time()
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
    all_sources = set()
    for company in companies:
        video_ids = youtube_search(company)
        company_comments = []
        for video_id in video_ids:
            comments = scrape_youtube_comments(video_id)
            if comments:
                company_comments.append(comments)
                all_sources.add(video_id)
        all_comments.extend(company_comments)
        # all_other_content.extend(company_other_content)

    print("got the results of length: ", len(all_comments))
    prompt = f"I am doing market research on these companies: {companies} in these industries: {industries}. These are a collection of youtube comments about these companies: {all_comments}. I am trying to create a startup; can you consolidate a list of top 10 desires of users that would be good startup ideas based on these comments and articles? Return only the list please."
    print("prompt", prompt)
    result = query_openai(prompt)
    print("top desires results", result)
    my_list = result.split('\n')

    # Remove numbers from each element in the list
    desires = [item.split('. ', 1)[1] if item.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) else item for item in my_list]
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.5f} seconds")
    return jsonify({"desires": desires, "sources": list(all_sources)}) # company and description

    
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



