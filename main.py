import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit



def check_for_redirect(response):
    if response.url == "https://tululu.org/":
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    filename = sanitize_filename(filename)
    response = requests.get(url)
    try:
        check_for_redirect(response) 
    except requests.exceptions.HTTPError as e:  
        return None
    response.raise_for_status() 
    if not os.path.exists(folder):
        os.makedirs(folder)
    str =  os.path.join(folder,f'{filename}')
    with open(str, 'wb') as file:
        file.write(response.content)
    return str


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    try:
        check_for_redirect(response) 
    except requests.exceptions.HTTPError as e:  
        return None
    
    response.raise_for_status() 
    if not os.path.exists(folder):
        os.makedirs(folder)
    str = os.path.join(folder,f'{filename}')
    with open(str, 'wb') as file:
        file.write(response.content)
    return str

if __name__ == "__main__":
    for i in range(5,11):
        response = requests.get(f"https://tululu.org/b{i}")
        try:
            check_for_redirect(response) 
        except requests.exceptions.HTTPError as e:  
            continue
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'lxml')
        url = urljoin('https://tululu.org',soup.find(class_='bookimage').find('a').find('img')['src'])
        download_image(url, urlsplit(url).path.split("/")[-1])
        #download_txt(f"https://tululu.org/txt.php?id={i}", f'{i}. {title.text.partition(" - ")[0].strip()}.txt', folder='books/')
        #title = soup.find('title')
        #print(f"Заголовок:{title.text.partition(' - ')[0].strip()}\nАвтор:{title.text.partition(' - ')[2].split(',')[0].strip()}")
        