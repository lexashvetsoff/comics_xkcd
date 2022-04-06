import requests
import os
from urllib.parse import urlsplit
from pathvalidate import sanitize_filename

URL_COMICS = 'https://xkcd.com/353/info.0.json'


def load_image(url, filename, folder='images', params={}):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)

    response = requests.get(url, params=params)
    response.raise_for_status()

    with open(path, 'wb') as file:
        file.write(response.content)


response = requests.get(URL_COMICS)
response.raise_for_status()

comics = response.json()
url_split = urlsplit(comics['img'])
file_name = sanitize_filename(url_split.path)

load_image(comics['img'], file_name)

author_comment = comics['alt']
print(author_comment)
