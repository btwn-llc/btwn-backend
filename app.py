from flask import Flask, jsonify, request
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

app = Flask(__name__)

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
    
    # Get the top products for the given industries
    top_companies = web_search(f"What are the top products belonging in these industries: {', '.join(industries)}")
    print(top_companies)
    
    return jsonify({"industries": industries, "top_companies": top_companies}) # company and description


if __name__ == '__main__':
    app.run(debug=True)
    # results = get_ai_snippets_for_query("reasons to smile")
    # print(results)



