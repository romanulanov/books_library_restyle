import json
import os
from livereload import Server, shell
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
import math


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open('books.json', encoding='utf-8') as json_file:
        books = json.load(json_file)
    num_pages = math.ceil(len(books)/10)
    books = list(chunked(books, 10))
    os.makedirs('pages/', exist_ok=True)

    for index, books in enumerate(books, 1):
        rendered_page = template.render(books=list(chunked(books, 2)),
                                        num_pages=range(1, num_pages+1),
                                        cur_page=index,
                                        )
        with open(f'pages/index{index}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

    server = Server()
    server.watch('template.html', shell('make html', cwd='docs'))
    server.serve(root='.')


if __name__ == "__main__":
    main()
