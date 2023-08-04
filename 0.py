
from bs4 import BeautifulSoup
import requests


response = requests.get("https://tululu.org/b8467/")
soup = BeautifulSoup(response.content, 'lxml')

print("Текст этой книги отсутствует" in str(soup))
#print("Текст этой книги отсутствует" in book_soups)