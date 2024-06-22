import requests
from bs4 import BeautifulSoup

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
