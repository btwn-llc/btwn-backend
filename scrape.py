import requests
from bs4 import BeautifulSoup
import json, os
import re
from dotenv import load_dotenv
load_dotenv('.env.local')

def get_youtube_id(url):

    # Regular expression pattern to match the video ID
    pattern = r"(?<=v=)[\w-]+"

    # Use re.search to find the pattern in the URL
    match = re.search(pattern, url)

    if match:
        video_id = match.group(0)
        print("Video ID:", video_id)
        return video_id
    else:
        print("Video ID not found")
        return None


def scrape_article_content(url):
    try:
        # Send HTTP request to fetch the webpage
        response = requests.get(url)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example: Extracting content from <p> tags (adjust based on HTML structure of the website)
            paragraphs = soup.find_all('p')
            
            # Combine paragraphs into one string (you may need more sophisticated logic depending on the site)
            content = '\n'.join([para.get_text() for para in paragraphs])
            return content[:3000]
        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while scraping {url}: {e}")
        return None

#openai_key: "str|None" = os.environ.get("OPENAI_API_KEY")
youtube_key = os.environ.get("YOUTUBE_API_KEY")

def scrape_youtube_comments(url):
    video_id = get_youtube_id(url)
    if not video_id:
        return None
    # Endpoint URL
    url = f'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={youtube_key}'

    try:
        # Send GET request
        response = requests.get(url)
        print("url", url, "response", response)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            # Example: Print first comment snippet
            if 'items' in data:
                for item in data['items']:
                    snippet = item['snippet']['topLevelComment']['snippet']
                    print(f"Author: {snippet['authorDisplayName']}")
                    print(f"Comment: {snippet['textOriginal']}")
                    print("------------------")
                    return snippet['textOriginal']
        else:
            print(f"Failed to fetch comments. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")

