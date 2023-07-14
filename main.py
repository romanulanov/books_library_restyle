import argparse
import requests
import os
import logging
import sys
from time import sleep
from bs4 import BeautifulSoup
from argparse import RawTextHelpFormatter
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.url == "https://tululu.org/":
        raise requests.exceptions.HTTPError


def download_txt(url, params, filename, folder='books/'):
    filename = sanitize_filename(filename)
    response = requests.get(url, params)
    response.raise_for_status()
    check_for_redirect(requests.get(url, params))
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, f'{filename}')
    with open(full_path, 'wb') as file:
        file.write(response.content)
    return full_path


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(requests.get(url))
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
        "Title": title.text.partition(' - ')[0].strip(),
        "Author": title.text.partition(' - ')[2].split(',')[0].strip(),
        "Genre": genres, 
        "Comments": comments,
        "Cover": image_url,
        }
    return book


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description='''Программа для скачивания книг с сайта https://tululu.org
        .\nБез заданных значений скачает по умолчанию с 1 по 10 книги:\n
        python main.py\nДля того, чтобы скачать книги, задайте значения
        для --start_id и --end_id, например команда: \n
        python main.py --start_id = 20 --end_id=30\n
        скачает с 20 по 30 книги.''',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--start_id',  default=1, type=int, help='Введите id книги, c которой начнётся скачивание (по умолчанию 1)')
    parser.add_argument('--end_id',  default=10, type=int, help='Введите id книги, на котором скачивание закончится (по умолчанию 10)')
    args = parser.parse_args()
    for index in range(args.start_id, args.end_id + 1):
        while True:
            try:
                response = requests.get(f"https://tululu.org/b{index}")
                response.raise_for_status()
                check_for_redirect(requests.get(response.url))
                book = parse_book_page(response)
                download_txt('https://tululu.org/txt.php', {"id": index}, f'{index}. {book["Title"]}.txt')
                download_image(book['Cover'], f'{index}.jpg')
                print(f'Название: {book["Title"]}\nАвтор: {book["Author"]}\n')
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
