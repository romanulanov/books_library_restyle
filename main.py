import argparse
from argparse import RawTextHelpFormatter
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


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
    str =  os.path.join(folder, f'{filename}')
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


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    title = soup.find('title')
    image_url = urljoin('https://tululu.org', soup.find(class_='bookimage').find('a').find('img')['src'])
    genres, comments = [], []
    for genre in soup.find_all(class_="d_book"):
            if genre.find('a') and "Жанр книги:" in genre.text:
                genres = (genre.text).split("Жанр книги: \xa0")[-1].strip().split(",")
    comments_soup = soup.find_all(class_='texts')
    if comments_soup:
        for comment in comments_soup:
            comments.append(comment.find(class_='black').text)
    else:
        comments.append(" ")
    book = {"Заголовок": title.text.partition(' - ')[0].strip(), "Автор": title.text.partition(' - ')[2].split(',')[0].strip(), "Жанр": genres, "Обложка": image_url, "Комментарии": comments}
    return book
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='''Программа для скачивания книг с сайта https://tululu.org.\nБез заданных значений скачает по умолчанию с 1 по 10 книги:\npython main.py\nДля того, чтобы скачать книги, задайте значения для --start_id и --end_id, например команда: \npython main.py --start_id = 20 --end_id=30\nскачает с 20 по 30 книги.''', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--start_id',  default=1, type = int, help='Введите id книги, c которой начнётся скачивание (по умолчанию 1)')
    parser.add_argument('--end_id',  default=10, type = int, help='Введите id книги, на котором скачивание закончится (по умолчанию 10)')
    args = parser.parse_args()
    for i in range(args.start_id, args.end_id + 1):
        response = requests.get(f"https://tululu.org/b{i}")
        try:
            check_for_redirect(response) 
        except requests.exceptions.HTTPError as e:  
            continue
        response.raise_for_status()  
        book = parse_book_page(response.content)
        if download_txt(f"https://tululu.org/txt.php?id={i}", f'{i}. {book["Заголовок"]}.txt') != None:
            download_txt(f"https://tululu.org/txt.php?id={i}", f'{i}. {book["Заголовок"]}.txt')
            print(f'Название: {book["Заголовок"]}\nАвтор: {book["Автор"]}\n')
