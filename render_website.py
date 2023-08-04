import argparse
import json
import math
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked


NUM_ROWS = 2
NUM_BOOKS_PER_PAGE = 10


def main():
    parser = argparse.ArgumentParser(
        description='')
    parser.add_argument('--dest_json',
                        default="books.json",
                        type=str,
                        help='Введите путь к каталогу с данными сайта (по умолчанию стоит файл books.json из корня проекта)',
                        )
    args = parser.parse_args()

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    

    

    

    def rebuild():
        template = env.get_template('template.html')
        with open(args.dest_json, encoding='utf-8') as json_file:
            books = json.load(json_file)
        num_pages = math.ceil(len(books)/NUM_BOOKS_PER_PAGE)
    
        os.makedirs('pages/', exist_ok=True)
        books = list(chunked(books, NUM_BOOKS_PER_PAGE))
        for index, books in enumerate(books, 1):
            print(index)
            rendered_page = template.render(books=list(chunked(books, NUM_ROWS)),
                                        num_pages=range(1, num_pages+1),
                                        cur_page=index,
                                        )
            with open(f'pages/index{index}.html', 'w', encoding='utf8') as file:
                file.write(rendered_page)
        

    rebuild()

    server = Server()
    server.watch('template.html', rebuild )
    server.serve(root='.')


if __name__ == "__main__":
    main()
