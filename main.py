import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import validate_filename, sanitize_filename

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
    
url = 'http://tululu.org/txt.php?id=1'



for i in range(1,11):
    #url = f"https://tululu.org/txt.php?id={i}"
    url = f"https://tululu.org/b{i}"
    response = requests.get(url)
    
    response.raise_for_status()  
    
    soup = BeautifulSoup(response.content, 'lxml')
    title = soup.find('title')
    download_txt(f"https://tululu.org/txt.php?id={i}", f'{i}. {title.text.partition(" - ")[0].strip()}.txt', folder='books/')
    #print(f"Заголовок:{title.text.partition(' - ')[0].strip()}\nАвтор:{title.text.partition(' - ')[2].split(',')[0].strip()}")
      
   
          
    


    
    