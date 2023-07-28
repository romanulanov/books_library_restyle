import json
from livereload import Server, shell
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open('books.json', encoding='utf-8') as json_file:
    books = json.load(json_file)  
books = list(chunked(books, 2))
print(books)
rendered_page = template.render(books=books)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)


server = Server()

server.watch('template.html', shell('make html', cwd='docs'))

server.serve(root='.')