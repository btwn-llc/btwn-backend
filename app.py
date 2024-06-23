from flask import Flask, jsonify, request
import os
import requests
from flask_cors import CORS
import llm
import PyPDF2
import io
import json
from dotenv import load_dotenv
from scrape import scrape_article_content, scrape_youtube_comments, youtube_search, App_Store_Scraper
from llm import query_openai
import time
from supa_client import SupaAdminClient
from threading import Thread
import re

load_dotenv('.env.local')

app = Flask(__name__)
CORS(app)


class User:
    def __init__(self, user_id: str):
        self.resumes = []

        supa = SupaAdminClient.get()
        data, count = supa.table("resume_strings").select("*").eq("owner", user_id).execute()
        resumes_list_raw = data[1]
        for elem in resumes_list_raw:
            self.resumes.append(elem['resume'])
        

def get_session_id() -> str|None:
    session_id = request.headers.get('session_id')
    return session_id



@app.route('/submit_resumes', methods=['POST'])
def submit_resumes():
    try:
        print("submit resumes")

        if request.files is None:
            return jsonify({"error": "No files provided"}), 400

        if 'resumes' not in request.files:
            return jsonify({"error": "No resume files provided"}), 400

        session_id: str|None = get_session_id()
        #ahh

        print("session_id: ", session_id)

        if not session_id:
            return jsonify({"error" : "No session_id providded"}), 400
        print("getting session")

        print("getting resumes")
        
        resumes = request.files.getlist('resumes')

        parsed_resumes: 'list[str]' = []
        
        num_resumes_submitted: int = 0
        for resume in resumes:
            if not resume.filename:
                continue
            if resume.filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                parsed_resumes.append(text)
                num_resumes_submitted += 1

        # extract names from each resume
        names: "list[str]" = []
        def resume_slab(resume):
            prompt: str = "Extract the name of the owner of the resume. Make sure the name is in right format(first letter capitalized.). Only provide the name and say nothing else. Name: \n" + resume
            extracted_name: str = llm.query_openai(prompt)
            nonlocal names
            names.append(extracted_name)
            print("Extracted name: ", extracted_name)
        try:
            workers = []
            for resume in parsed_resumes:
                t = Thread(target = resume_slab, args=(resume,))
                t.start()
                workers.append(t)
            for t in workers:
                t.join()
        except Exception as e:
            print("Error extracting names: ", str(e))
            return jsonify({"error", "Error extracting names from resume"}), 500

        # add the resumes to db
        supa = SupaAdminClient.get()
        table = supa.table("resume_strings")
        for resume in parsed_resumes:
            table.insert({"owner": session_id, "resume": resume}).execute()
        
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

    session: User = User(session_id) # type: ignore

    if len(session.resumes) == 0:
        return jsonify({"errors": "No resumes submitted"}), 400

    industries: 'set[str]' = set()

    def slab(resume):
        prompt: str = f"{resume} \n Above is a text resume of a person, Please extract at most three industries that the person could be a good fit for. \
                return the industries as a parseable string list, with a emoji for each industry, such as [🏥 healthcare, 🍀 environment, 💻 technology]. Only return the bracked list and nothing else.\
                list: ".format(resume=resume)
        llm_response: str = llm.query_openai(prompt)
        llm_resopnse_parsed = parse_llm_response(llm_response)
        nonlocal industries
        industries.update(llm_resopnse_parsed)
        # parse the response in form of [industyr1, industry2, industry3]
    workers = []
    for resume in session.resumes:
        t = Thread(target=slab, args=(resume,))
        t.start()
        workers.append(t)
    for t in workers:
        t.join()

    industries_ls: 'list[str]' = list(industries)
    
    return jsonify({"industries": industries_ls}), 200


@app.route('/')
def hello():
    return jsonify({"message": "bye!"})

@app.route('/search/<query>', methods=['GET'])
def web_search(query, num_results=20):
    headers = {"X-API-Key": os.environ.get('YOU_WEB_SEARCH_API')}
    params = {"query": query, "country": "US", "num_web_results": num_results}
    print("headers", headers)
    req = requests.get(
        f"https://api.ydc-index.io/search",
        params=params,
        headers=headers,
    )
    result = req.json()
    return result

@app.route('/top-ideas', methods=['POST'])
def top_ideas():
    #here
    start_time = time.time()
    data = request.json
    complaints = data['complaints']
    user_notes = data["user_notes"]
    industries = data["industries"]
    # list of top complaints reordered
    prompt = f'''
    I am trying to create a new startup in these industries: {{industries}}. Here are my ideas {{user_notes}}. Can you brainstorm potential solutions/products based on my notes and on the complaints from customers THAT I ORDERED FROM MOST IMPORTANT TO LEAST IMPORTANT: {{complaints}}, and place emphasis on the MOST IMPORTANT complaints. Return a json list. Example:
    [
        {{
            "title": "create a more environmental-friendly packaging service",
            "detail": "Develop a sustainable packaging service offering eco-friendly alternatives to traditional materials. Use biodegradable and compostable options, implement a reusable packaging system, and provide custom-sized solutions to minimize waste. Offer recycling programs and consulting services to help businesses transition to greener packaging. Cater to e-commerce, food delivery, and retail sectors aiming to reduce environmental impact and appeal to eco-conscious consumers."
        }},
        {{
            "title": "launch a virtual reality language learning platform",
            "detail": "Develop an immersive VR platform for language learning, allowing users to practice conversations in realistic virtual environments. Include AI-powered language partners, cultural experiences, and gamified lessons to make language acquisition more engaging and effective."
        }}
    ]
    return only the json and say nothing else.
    json: 
    '''
    print("prompt", prompt)
    result = query_openai(prompt)
    print("RESULT", result)

    return jsonify({"solutions":result})


def top_complaints_worker(session_id: str, data):
    start_time = time.time()

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
    
    # Ensure the list contains at most 3 companies
    if len(companies) > 3:
        return jsonify({"error": "You can provide a maximum of 3 companies."}), 400

    print("chosen companies", companies)
    all_sources = set()
    all_comments = []
    def company_slab(company):
        nonlocal all_sources
        nonlocal all_comments
        
        # check youtube
        company_comments = []

        video_ids = youtube_search(company) or []

        def youtube_slab(video_id):
            comments = scrape_youtube_comments(video_id)
            if comments:
                nonlocal company_comments
                nonlocal all_sources
                company_comments.extend(comments)
                all_sources.add(video_id)

        company_workers = []

        for video_id in video_ids:
            t = Thread(target=youtube_slab, args=(video_id,))
            t.start()
            company_workers.append(t)
            
        # check app store next
        # def app_store_slab():
        #     scraper_instance = App_Store_Scraper('us', company)
        #     scraper_instance.review(num_pages=10, max_rating=1, after=None, sleep=1)
        #     for review in scraper_instance.reviews:
        #         company_comments.append(review["content"])
        # app_store_worker = Thread(target=app_store_slab)
        # app_store_worker.start()
        # company_workers.append(app_store_worker)
        # Get the top companies for the given industries

        web_search_results = web_search(f"Company: {company}", num_results=20)

        # Scrape top 5 links
        texts = []

        def result_slab(result):
            nonlocal texts
            link = result["url"]
            if len(texts) >= 1:
                return
            article_result = scrape_article_content(link)
            if article_result:
                texts.append(article_result)
                print("Successfully retrieved: ", link)

        for result in web_search_results["hits"]:
            t = Thread(target= result_slab, args=(result,))
            t.start()
            company_workers.append(t)

        for t in company_workers:
            t.join(timeout=20)

        # prompt = f"Can you return a detailed background on this company {company} based on these texts: {texts}"
        # company_context = query_openai(prompt)
        prompt = f"This is background on company {company} from a selection of texts: {texts}. \n\n\n\n These are a collection of youtube and app store comments on this company: {company_comments}. Can you consolidate a list of top 10 complaints from users based on these comments, and cite the specific comments that were used to generate the complaints?"
        complaints = query_openai(prompt)
        all_comments.append(complaints)

    threads = []
    for company in companies:
        t = Thread(target = company_slab, args=(company,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=20)

    
    prompt = f"""Generate a JSON array of the top 10 complaints for a startup rivaling these companies: {companies}. Base the complaints on this data: {all_comments}. Format each complaint as an object with 'title' and 'directComments' fields. The 'directComments' should be an array of relevant quotes from the input data. Respond only with the JSON array, no additional text. Example format:

    [
    {{
    "title": "Complaint Title",
    "directComments": [
    "Relevant quote 1",
    "Relevant quote 2"
    ]
    }},
    ...
    ]
    json array: \n
    """
    print("prompt", prompt)
    result = query_openai(prompt)

    # only take the stuff in between ``` and ```
    if "```" in result:
        result = result.split("```")[1]

    # append result to db
    supa = SupaAdminClient.get()
    supa.table("top_complaints_cache").insert({"session_id": session_id, "data": result}).execute()

    # dana stuff begin
            # print("top desires results", result)
            # my_list = result.split('\n')
            #
            # # Remove numbers from each element in the list
            # desires = [item.split('. ', 1)[1] if item.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) else item for item in my_list]
            # end_time = time.time()
            # print(f"Execution time: {end_time - start_time:.5f} seconds")
            # return jsonify({"complaints": desires, "comments": all_comments, "sources": list(all_sources)}) # company and description
    # dana stuff end

@app.route('/retrieve-top-complaints', methods=['POST'])
def retrieve_top_complaints():
    session_id : str| None = get_session_id()
    if session_id is None:
        return jsonify({"error": "no sessino_id provided"}), 400
    supa = SupaAdminClient.get()
    data, count = supa.table("top_complaints_cache").select("*").eq("session_id", session_id).execute()
    print("data from retrieve_top_complaints: ", data)
    return jsonify({"top_complaints": data[1][0]}), 200



@app.route('/top-complaints', methods=['POST'])
def top_complaints():
    # session_id = get_session_id()
    # if session_id is None:
    #     return jsonify({"error": "No session_id provided"}), 400

    session_id: str = get_session_id() #type: ignore
    data = request.json

    t = Thread(target=top_complaints_worker, args=(session_id, data))
    t.start() # the thread will run

    return jsonify({"hello": "bhada"})

    
@app.route('/top-companies', methods=['POST'])
def top_companies():
    data = request.json
    #
    
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
    def scraper(result):
        link = result["url"]
        if len(top_companies_result) >= 3:
            return
        article_result = scrape_article_content(link)
        if article_result:
            top_companies_result.append(article_result)
            print("Successfully retrieved: ", link)

    top_companies_result = []
    workers = []
    for result in results["hits"]:
        t = Thread(target=scraper, args=(result,))
        t.start()
        workers.append(t)

    for worker in workers:
        worker.join(timeout=10)


    # Filter with OpenAI
    prompt = f"Can you glean the top 10 companies from these results along with a description of them and format it into a list of dictionaries with keys of company_name and company description: {top_companies_result}. JUST RETURN THE LIST ONLY WITH NO OTHER COMMENTS. List: \n"
    result = query_openai(prompt)
    # Extract JSON using a regular expression
    json_match = re.search(r'\[.*\]', result, re.DOTALL)

    if json_match:
        json_str = json_match.group(0)
        try:
            parsed_result = json.loads(json_str)
            print("Parsed Result:", parsed_result)
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
    else:
        print("No JSON found in the response")
    # result = json.loads(parsed_result)
    return jsonify({"industries": industries, "top_companies": parsed_result}) # company and description

@app.route('/solution-candidate-fit', methods=['POST'])
def solution_candidate_fit():
    session_id: str|None = get_session_id()
    if session_id is None:
        return jsonify({"error" : "No session)_id provided"}), 400

    solution: str = request.json["solution"] # type: ignore
    session = User(session_id)
    if len(session.resumes) == 0:
        return jsonify({'error': 'No resumes submitted'}), 400

    history = [
            {"role" : "user", "text" : "here is a solution that I came up with for a problem: \n" + solution},
            {"role" : "user", "text" : "following is a list of resumes of the candidaetes that may be a good fit for the solution: \n" + str(session.resumes)},
            {"role" : "user", "text" : "please provide a list of the top 3 candidates taht may be a good fit for the solution, and why they are a good fit"},
    ]
    candidate_recs : str = llm.query_openai("", history=history)

    candidates_formatted: str = llm.query_openai(\
            f"{candidate_recs}the above is a list of candidates, and the reasons why they are good. Please format the candidates into a list of json with key 'name' mapped to the name and 'reason' mapped to the reason they are selected. Example: \
json```\
[\
{{'name': 'John Doe', 'reason' : 'John has experience in the field of AI and has worked on similar projects in the past.'}},\
{{'name': 'Bhada Yun', 'reason' : 'Bhada has a strong background in machine learning and has interest in data science.'}}\
]\
```\
json: \n")
    candidates = json.loads(candidates_formatted)

    return jsonify({"candidates": candidates}), 200

if __name__ == '__main__':
    app.run(debug=True)
    # results = get_ai_snippets_for_query("reasons to smile")
    # print(results)
