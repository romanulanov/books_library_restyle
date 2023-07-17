import requests
import json
import argparse
import os
import logging
import sys
from time import sleep
from bs4 import BeautifulSoup
from argparse import RawTextHelpFormatter
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlencode


def check_for_redirect(url):
    if url == "https://tululu.org/":
        raise requests.exceptions.HTTPError


def download_txt(url, params, filename, folder='books/'):
    filename = sanitize_filename(filename)
    response = requests.get(url, params)
    response.raise_for_status()
    check_for_redirect(response.url)
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, f'{filename}')
    with open(full_path, 'wb') as file:
        file.write(response.content)
    return full_path


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(url)
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, f'{filename}')
    with open(full_path, 'wb') as file:
        file.write(response.content)
    return full_path


def parse_book_page(response):
    html_content = response.content
    soup = BeautifulSoup(html_content, 'lxml')
    title = soup.select_one("title")
    image_url = urljoin(response.url, soup.select_one('.bookimage a img')['src'])
    genres, comments = [], []
    for genre in soup.select(".d_book"):
        if genre.select_one('a') and "Жанр книги:" in genre.text:
            genres = (genre.text).split("Жанр книги: \xa0")[-1].strip().split(",")
    comments_soup = soup.select('.texts')
    for comment in comments_soup:
        comments.append(comment.select_one('.black').text)
    book = {
        "title": title.text.partition(' - ')[0].strip(),
        "author": title.text.partition(' - ')[2].split(',')[0].strip(),
        "img_src": image_url,
        "book_path": f"books/{title.text.partition(' - ')[0].strip()}.txt",
        "comments": comments,
        "genres": genres, 
        }
    return book


def main():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description='''Программа для скачивания книг с сайта https://tululu.org
        .\nБез заданных значений скачает по умолчанию с 1 по 10 книги:\n
        python main.py\nДля того, чтобы скачать книги, задайте значения
        для --start_id и --end_id, например команда: \n
        python main.py --start_id = 20 --end_id=30\n
        скачает с 20 по 30 книги.''',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--start_page',  default=1, type=int, help='Введите id книги, c которой начнётся скачивание (по умолчанию 1)')
    parser.add_argument('--end_page',  default=702, type=int, help='Введите id книги, на котором скачивание закончится (по умолчанию 10)')
    args = parser.parse_args()
    
    books, books_url = [], []
    for page_num in range(args.start_page, args.end_page + 1):
        response = requests.get(f"https://tululu.org/l55/{page_num}")
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        book_soups = soup.select(".ow_px_td")
        for book in book_soups:
            for book_url in book.select('a'):
                if '/b' in book_url['href'] and urljoin("https://tululu.org/", book_url['href']) not in books_url:
                    books_url.append(urljoin("https://tululu.org/", book_url['href']))
        
    
    for book_url in books_url:
        while True:
            try:
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response.url)
                book = parse_book_page(response)
                books.append(book)
                path = urlparse(book_url).path
                index = path[path.find('b')+1:-1]
                download_txt('https://tululu.org/txt.php', {"id": index}, f'{index}. {book["title"]}.txt')
                download_image(book['img_src'], f'{index}.jpg')
                print(book_url)
                break
            except requests.exceptions.HTTPError:
                logging.error('Ошибка ссылки у книги. Попробую скачать следующую.')
                print(f'{sys.stderr}\n')
                break
            except requests.exceptions.ConnectionError:
                logging.error('Ошибка сети. Попробую переподключиться через минуту.')
                print(f'{sys.stderr}\n')
                sleep(60)
                continue
    with open('books.json', 'w', encoding='utf8') as json_file:
        json.dump(books, json_file, ensure_ascii=False)    


if __name__ == "__main__":
    main()