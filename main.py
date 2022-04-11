from tokenize import group
from urllib import response
import requests
import os
from urllib.parse import urlsplit
from pathvalidate import sanitize_filename
from dotenv import load_dotenv
from random import randint

URL_LAST_COMICS = 'https://xkcd.com/info.0.json'

URL_API_VK_PHOTO_SERVER = 'https://api.vk.com/method/photos.getWallUploadServer'
URL_API_VK_SAVE_PHOTO = 'https://api.vk.com/method/photos.saveWallPhoto'
URL_API_VK_PUBLICATION_PHOTO = 'https://api.vk.com/method/wall.post'


def load_image(url, filename, folder='images', params={}):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)

    response = requests.get(url, params=params)
    response.raise_for_status()

    with open(path, 'wb') as file:
        file.write(response.content)
    
    return path


def get_last_comics(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_random_url_comics():
    last_comics = get_last_comics(URL_LAST_COMICS)
    num_comics = randint(1, last_comics)
    return f'https://xkcd.com/{num_comics}/info.0.json'


def get_comics():
    response = requests.get(get_random_url_comics())
    response.raise_for_status()

    comics = response.json()

    url_split = urlsplit(comics['img'])
    file_name = sanitize_filename(url_split.path)

    return load_image(comics['img'], file_name), comics['alt']


def get_server(group_id, access_token):
    payload = {
        'group_id': group_id,
        'access_token': access_token,
        'v': 5.131
    }

    response = requests.get(URL_API_VK_PHOTO_SERVER, params=payload)
    response.raise_for_status()

    return response.json()['response']['upload_url']


def upload_img_to_server(img_path, photo_server):
    with open(img_path, 'rb') as file:
        url = photo_server
        files = {
            'photo': file
        }

        response = requests.post(url, files=files)
        response.raise_for_status()

    return response.json()['server'], response.json()['photo'], response.json()['hash']


def save_img_to_server(group_id, server, photo, hash, access_token):
    payload = {
        'group_id': group_id,
        'server': server,
        'photo': photo,
        'hash': hash,
        'access_token': access_token,
        'v': 5.131,
    }

    response = requests.post(URL_API_VK_SAVE_PHOTO, params=payload)
    response.raise_for_status()

    return response.json()['response'][0]['owner_id'], response.json()['response'][0]['id']


def publication_img(owner_id, photo_id, group_id, author_comment, access_token):
    attachments = 'photo{}_{}'.format(owner_id, photo_id)
    payload = {
        'owner_id': -int(group_id),
        'from_group': 1,
        'attachments': attachments,
        'message': author_comment,
        'access_token': access_token,
        'v': 5.131
    }

    response = requests.get(URL_API_VK_PUBLICATION_PHOTO, params=payload)
    response.raise_for_status()
    print(response.json())


def main():
    load_dotenv()
    
    try:
        access_token = os.getenv('ACCESS_TOKEN')
        group_id = os.getenv('PUBLIC_ID')

        img_path, author_comment = get_comics()
        photo_server = get_server(group_id, access_token)
        server, photo, photo_hash = upload_img_to_server(img_path, photo_server)
        owner_id, photo_id = save_img_to_server(group_id, server, photo, photo_hash, access_token)

        publication_img(owner_id, photo_id, group_id, author_comment, access_token)
    finally:
        os.remove(img_path)


if __name__ == '__main__':
    main()
