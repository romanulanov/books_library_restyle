import json
import ast
from livereload import Server, shell

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open('books.json', encoding='utf-8') as json_file:
    books = json.load(json_file)  

rendered_page = template.render(books=books)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)


server = Server()

server.watch('template.html', shell('make html', cwd='docs'))

server.serve(root='.')