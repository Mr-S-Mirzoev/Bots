from bs4 import BeautifulSoup
import requests

url = 'https://www.xnxx.com/tags' # going through pages.
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
redditAll = soup.find_all("a")
categories = set()
for links in soup.find_all('li'):
    html_part = str(links.a)
    category = html_part[html_part.find('>') + 1 : html_part.find('<', 1)]
    categories.add(category)
with open("./metainfo/categories.txt", 'w') as f:
    for category in categories:
        f.write(category + '\n')
