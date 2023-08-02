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
from urllib.parse import urljoin, urlparse, quote


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
        "img_src": f"/images/{response.url.split('/b')[1][:-1]}.jpg",
        "book_path": quote(f"/books/{response.url.split('/b')[1][:-1]}. {title.text.partition(' - ')[0].strip()}.txt"),
        "comments": comments,
        "genres": genres,
        }
    return book


def main():
    parser = argparse.ArgumentParser(
        description='''Программа для скачивания книг в жанре научной фантастики
        с сайта https://tululu.org.\nБез заданных значений скачает все книги
        с 1 по 701 страницу.\n
        python main.py\nДля того, чтобы скачать книги, задайте значения
        для --start_page и --end_page, например команда: \n
        python main.py --start_page = 20 --end_page=30\n
        скачает книги с 20 по 30 страницу.''',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--start_page',
                        default=1,
                        type=int,
                        help='Введите номер страницы, c которой начнётся скачивание (по умолчанию 1)',
                        )
    parser.add_argument('--end_page',
                        default=702,
                        type=int,
                        help='Введите номер страницы, на котором скачивание закончится (по умолчанию 701)',
                        )
    parser.add_argument('--dest_folder',
                        default="",
                        type=str,
                        help='Введите путь к каталогу с результатами парсинга (по умолчанию всё сохраняется в корневой каталог проекта)',
                        )
    parser.add_argument('--skip_imgs',
                        default=False,
                        action='store_true',
                        help='Введите в запросе --skip_imgs, чтобы не скачивать картинки',
                        )
    parser.add_argument('--skip_txt',
                        default=False,
                        action='store_true',
                        help='Введите в запросе --skip_txt, чтобы не скачивать книги',
                        )
    args = parser.parse_args()

    books, book_urls = [], []
    for page_num in range(args.start_page, args.end_page + 1):
        while True:
            try:
                response = requests.get(f"https://tululu.org/l55/{page_num}")
                response.raise_for_status()
                check_for_redirect(response.url)
                soup = BeautifulSoup(response.content, 'lxml')
                book_soups = soup.select(".ow_px_td")
                for book in book_soups:
                    for book_url in book.select('a'):
                        if '/b' in book_url['href'] and urljoin("https://tululu.org/", book_url['href']) not in book_urls:
                            book_urls.append(urljoin("https://tululu.org/", book_url['href']))
                break
            except requests.exceptions.HTTPError:
                logging.error('Ошибка ссылки у страницы. Попробую скачать следующую.')
                print(f'{sys.stderr}\n')
                break
            except requests.exceptions.ConnectionError:
                logging.error('Ошибка сети. Попробую переподключиться через минуту.')
                print(f'{sys.stderr}\n')
                sleep(60)
                continue

    for book_url in book_urls:
        while True:
            try:
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response.url)
                book = parse_book_page(response)
                books.append(book)
                url_path = urlparse(book_url).path
                index = url_path[url_path.find('b')+1:-1]

                params, filename = {"id": index}, f'{index}. {book["title"]}.txt'
                folder_book = 'books/'
                folder_image = 'images/'
                folder_json = ""
                if args.dest_folder:
                    folder_book = f'{args.dest_folder}/books/'.strip()
                    folder_image = f'{args.dest_folder}/images'.strip()
                    folder_json = f'{args.dest_folder}/'.strip()
                if args.skip_imgs:
                    download_txt('https://tululu.org/txt.php',  params, filename, folder_book)
                if args.skip_txt:
                    download_image(book['img_src'], f'{index}.jpg', folder_image)
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

    with open(f'{folder_json}books.json', 'w', encoding='utf8') as json_file:
        json.dump(books, json_file, ensure_ascii=False)


if __name__ == "__main__":
    main()
