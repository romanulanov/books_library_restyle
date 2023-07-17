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
    title = soup.find('title')
    image_url = urljoin(response.url, soup.find(class_='bookimage').find('a').find('img')['src'])
    genres, comments = [], []
    for genre in soup.find_all(class_="d_book"):
        if genre.find('a') and "Жанр книги:" in genre.text:
            genres = (genre.text).split("Жанр книги: \xa0")[-1].strip().split(",")
    comments_soup = soup.find_all(class_='texts')
    for comment in comments_soup:
        comments.append(comment.find(class_='black').text)
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
    books = []
    books_url = []
    for page_num in range(1, 2):
        response = requests.get(f"https://tululu.org/l55/{page_num}")
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        book_soups = soup.find_all(class_="ow_px_td")
        for book in book_soups:
            for book_url in book.find_all('a'):
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
                print(f'Название: {book["title"]}\nАвтор: {book["author"]}\n')
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
    print(books)

    with open('books.json', 'w', encoding='utf8') as json_file:
        json.dump(books, json_file, ensure_ascii=False)    

    #books = json.dumps(books, ensure_ascii=False)
    #with open("books.json", "w", encoding='utf8') as my_file:
    #    my_file.write(books, "\n" , ensure_ascii=False)


if __name__ == "__main__":
    main()