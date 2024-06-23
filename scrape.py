import requests
from bs4 import BeautifulSoup
import json, os
import re
from dotenv import load_dotenv
load_dotenv('.env.local')

#openai_key: "str|None" = os.environ.get("OPENAI_API_KEY")
youtube_key = os.environ.get("YOUTUBE_API_KEY")

def youtube_search(query):

    # Endpoint URL
    url = 'https://www.googleapis.com/youtube/v3/search'

    # Parameters for the request
    params = {
        'part': 'snippet',
        'q': query,
        'key': youtube_key,
        'maxResults': 20
    }

    try:
        # Send GET request
        response = requests.get(url, params=params)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            # Extract video IDs from items
            video_ids = [item['id']['videoId'] for item in data['items'] if item['id']['kind'] == 'youtube#video']
            
            # Print list of video IDs
            return video_ids
        else:
            print(f"Failed to fetch search results. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")


def get_youtube_id(url):

    # Regular expression pattern to match the video ID
    pattern = r"(?<=v=)[\w-]+"

    # Use re.search to find the pattern in the URL
    match = re.search(pattern, url)

    if match:
        video_id = match.group(0)
        return video_id
    else:
        print("Video ID not found with this url", url)
        return None


def scrape_article_content(url, max_length=3000):
    try:
        # Send HTTP request to fetch the webpage
        response = requests.get(url)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            paragraphs = soup.find_all('p')
            
            content = '\n'.join([para.get_text() for para in paragraphs])
            return content[:max_length]
        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while scraping {url}: {e}")
        return None

def scrape_youtube_comments(video_id):
    if not video_id:
        return None
    # Endpoint URL
    url = f'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={youtube_key}&maxResults=20'

    try:
        # Send GET request
        response = requests.get(url)
        print("url", url, "response", response)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            comments = []
            if 'items' in data:
                for item in data['items']:
                    snippet = item['snippet']['topLevelComment']['snippet']
                    comments.append(snippet['textOriginal'])
            return comments
        else:
            print(f"Failed to fetch comments. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")

