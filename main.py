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


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def download_txt(url, filename, folder='books/'):
    filename = sanitize_filename(filename)
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    str = os.path.join(folder, f'{filename}')
    with open(str, 'wb') as file:
        file.write(response.content)
    return str


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    str = os.path.join(folder, f'{filename}')
    with open(str, 'wb') as file:
        file.write(response.content)
    return str


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
    book = {"Title": title.text.partition(' - ')[0].strip(), "Author": title.text.partition(' - ')[2].split(',')[0].strip(), "Genre": genres, "Comments": comments, "Cover": image_url}
    return book


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='''Программа для скачивания книг с сайта https://tululu.org.\nБез заданных значений скачает по умолчанию с 1 по 10 книги:\npython main.py\nДля того, чтобы скачать книги, задайте значения для --start_id и --end_id, например команда: \npython main.py --start_id = 20 --end_id=30\nскачает с 20 по 30 книги.''', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--start_id',  default=1, type=int, help='Введите id книги, c которой начнётся скачивание (по умолчанию 1)')
    parser.add_argument('--end_id',  default=10, type=int, help='Введите id книги, на котором скачивание закончится (по умолчанию 10)')
    args = parser.parse_args()
    for index in range(args.start_id, args.end_id + 1):
        flag_error = False
        while True:
            response = requests.get(f"https://tululu.org/b{index}")
            try:
                check_for_redirect(response)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError:
                logging.error('Ошибка ссылки у книги. Попробую скачать следующую.')
                eprint(sys.stderr)
                flag_error = True
                break
            except requests.exceptions.ConnectionError:
                logging.error('Ошибка сети. Попробую переподключиться через минуту.')
                eprint(sys.stderr)
                sleep(60)
                pass
        if flag_error:
            continue
        book = parse_book_page(response)
        print(book)
        while True:
            try:
                check_for_redirect(requests.get('https://tululu.org/txt.php', params={"id": index}))
                result_download = download_txt(requests.get('https://tululu.org/txt.php', params={"id": index}).url, f'{index}. {book["Title"]}.txt')
                break
            except requests.exceptions.HTTPError:
                result_download = None
                break
            except requests.exceptions.ConnectionError:
                logging.error('Ошибка сети. Попробую переподключиться через минуту.')
                eprint(sys.stderr)
                sleep(60)
                pass
        if result_download:
            while True:
                try:
                    check_for_redirect(requests.get(book['Cover']))
                    break
                except requests.exceptions.HTTPError:
                    continue
                except requests.exceptions.ConnectionError:
                    logging.error('Ошибка сети. Попробую переподключиться через минуту.')
                    eprint(sys.stderr)
                    sleep(60)
                    pass
            download_image(book['Cover'], f'{index}.jpg')
            print(f'Название: {book["Title"]}\nАвтор: {book["Author"]}\n')
