from bs4 import BeautifulSoup
import requests


page = requests.get("https://en.wikipedia.org/wiki/Art")
soup = BeautifulSoup(page.content, 'html.parser')
