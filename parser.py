from bs4 import BeautifulSoup
import requests

url_xnxx = 'https://www.xnxx.com/tags' # going through pages.
response = requests.get(url_xnxx)

soup = BeautifulSoup(response.text, 'html.parser')
redditAll = soup.find_all("a")
categories_xnxx = set()
for links in soup.find_all('li'):
    html_part = str(links.a)
    category = html_part[html_part.find('>') + 1 : html_part.find('<', 1)]
    categories_xnxx.add(category)
with open("./metainfo/categories.txt", 'w') as f:
    for category in categories_xnxx:
        f.write(category + '\n')

url_itsporn = 'https://www.its.porn/categories'
response = requests.get(url_itsporn)

soup = BeautifulSoup(response.text, 'html.parser')
redditAll = soup.find_all("div", "categories_item")
for cat in redditAll:
    print(cat['a'])
"""
categories_itsporn = set()
for links in soup.find_all('li'):
    html_part = str(links.a)
    category = html_part[html_part.find('>') + 1 : html_part.find('<', 1)]
    categories_itsporn.add(category)
with open("./metainfo/categories.txt", 'w') as f:
    for category in categories_itsporn:
        f.write(category + '\n')
"""