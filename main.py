from tokenize import group
from urllib import response
import requests
import os
from urllib.parse import urlsplit
from pathvalidate import sanitize_filename
from dotenv import load_dotenv
from random import randint


def load_image(url, filename, folder='images', params={}):
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)

    response = requests.get(url, params=params)
    response.raise_for_status()

    with open(path, 'wb') as file:
        file.write(response.content)
    
    return path


def get_last_number_comics(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_random_url_comics():
    url_last_comics = 'https://xkcd.com/info.0.json'
    last_comics = get_last_number_comics(url_last_comics)
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
    url_api_vk_photo_server = 'https://api.vk.com/method/photos.getWallUploadServer'

    payload = {
        'group_id': group_id,
        'access_token': access_token,
        'v': 5.131
    }

    response = requests.get(url_api_vk_photo_server, params=payload)
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

        server = response.json()

    return server['server'], server['photo'], server['hash']


def save_img_to_server(group_id, server, photo, hash, access_token):
    url_api_vk_save_photo = 'https://api.vk.com/method/photos.saveWallPhoto'

    payload = {
        'group_id': group_id,
        'server': server,
        'photo': photo,
        'hash': hash,
        'access_token': access_token,
        'v': 5.131,
    }

    response = requests.post(url_api_vk_save_photo, params=payload)
    response.raise_for_status()

    return response.json()['response'][0]['owner_id'], response.json()['response'][0]['id']


def make_publication_img(owner_id, photo_id, group_id, author_comment, access_token):
    url_api_vk_publication_photo = 'https://api.vk.com/method/wall.post'

    attachments = 'photo{}_{}'.format(owner_id, photo_id)
    payload = {
        'owner_id': -int(group_id),
        'from_group': 1,
        'attachments': attachments,
        'message': author_comment,
        'access_token': access_token,
        'v': 5.131
    }

    response = requests.get(url_api_vk_publication_photo, params=payload)
    response.raise_for_status()


def main():
    load_dotenv()
    
    try:
        access_token = os.getenv('ACCESS_TOKEN')
        group_id = os.getenv('PUBLIC_ID')

        img_path, author_comment = get_comics()
        photo_server = get_server(group_id, access_token)
        server, photo, photo_hash = upload_img_to_server(img_path, photo_server)
        owner_id, photo_id = save_img_to_server(group_id, server, photo, photo_hash, access_token)

        make_publication_img(owner_id, photo_id, group_id, author_comment, access_token)
    finally:
        os.remove(img_path)


if __name__ == '__main__':
    main()
