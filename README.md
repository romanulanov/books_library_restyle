# Оффлайн библиотека книг с сайта tululu.org

![image](https://drive.google.com/uc?export=view&id=16Zmjfp5_0b341rt-X8Te2pvDmr-uGF7a)
Ссылка на сайт:[https://romanulanov.github.io/pages/index1.html](https://romanulanov.github.io/pages/index1.html).
Ссылка на репозиторий: [https://github.com/romanulanov/books_library_restyle](https://github.com/romanulanov/books_library_restyle).

Программа для вёрстки сайта-библиотеки в жанре научной фантастики.  

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Аргументы

Чтобы сверстать сайт вам понадобится json-каталог внутри проекта и файлы в папке media (внутри в папке books  хранятся txt книг, а в images их обложки). Напишите в окружении  
```
python render_website.py
```
и откройте первую страницу библиотеки по адресу [http://127.0.0.1:5500/pages/index1.html](http://127.0.0.1:5500/pages/index1.html). Страницы сайта хранятся в папке pages. 
Если у вас есть свой каталог, укажите полный путь к нему в dest_json, например:
```
python render_website.py --dest_json C:\Users\User\Desktop\books.json
```
Ниже описаны способы скачивания книг.
Без заданных значений программа будет скачивать все книги в жанре научной фантастики (с 1 по 701 страницу). Для этого напишите в окружении просто:
```
python parse_tululu_category.py
```
Укажите в start_page (по умолчанию задано 1) с какой страницы начать скачивание книг и в end_page (по умолчанию задано 701) номер последней страницы. Например, чтобы скачать книги с 20 по 30 страницу напишите в окружении:
```
python parse_tululu_category.py --start_page 20 --end_id 30 
```
Или если хотите скачать книги с какой-либо страницы по последнюю, задайте в окружении только start_page. Например, чтобы скачать все книги с 600-ой по последнюю страницу, напишите:
```
python parse_tululu_category.py --start_page 600
```
Если не хотите скачивать обложки к книгам, напишите в запросе skip_imgs. Например, чтобы скачать только книги без обложек с 20 по 30 страницу, напишите в окружении:
```
python parse_tululu_category.py --start_page 20 --end_id 30 --skip_imgs
```
Если не хотите скачивать сами книги, напишите в запросе skip_txt:
```
python parse_tululu_category.py --skip_txt
```
Чтобы скачать книги в определённую папку, задайте полный путь к каталогу с результатами парсинга в аргументе dest_folder:
```
python parse_tululu_category.py --dest_folder E:/games
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).