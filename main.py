import requests
import os

directory = "books/"
if not os.path.exists(directory):
    os.makedirs(directory)

for i in range(1,11):
    url = f"https://tululu.org/txt.php?id={i}"
    response = requests.get(url)
    response.raise_for_status() 
    filename = f'{directory}id{i}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)