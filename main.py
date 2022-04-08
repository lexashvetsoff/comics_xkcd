from tokenize import group
import requests
import os
from urllib.parse import urlsplit
from pathvalidate import sanitize_filename
from dotenv import load_dotenv

load_dotenv()

URL_COMICS = 'https://xkcd.com/353/info.0.json'

URL_API_VK_PHOTO_SERVER = 'https://api.vk.com/method/photos.getWallUploadServer'
URL_API_VK_SAVE_PHOTO = 'https://api.vk.com/method/photos.saveWallPhoto'
URL_API_VK_PUBLICATION_PHOTO = 'https://api.vk.com/method/wall.post'

access_token = os.getenv('ACCESS_TOKEN')
group_id = os.getenv('PUBLIC_ID')


def load_image(url, filename, folder='images', params={}):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)

    response = requests.get(url, params=params)
    response.raise_for_status()

    with open(path, 'wb') as file:
        file.write(response.content)
    
    return path


response = requests.get(URL_COMICS)
response.raise_for_status()

comics = response.json()
url_split = urlsplit(comics['img'])
file_name = sanitize_filename(url_split.path)

img_name = load_image(comics['img'], file_name)

author_comment = comics['alt']
# print(author_comment)

payload = {
    'group_id': group_id,
    'access_token': access_token,
    'v': 5.131
}

response = requests.get(URL_API_VK_PHOTO_SERVER, params=payload)
response.raise_for_status()

photo_server = response.json()['response']
# print(photo_server['upload_url'])
# print(img_name)

with open(img_name, 'rb') as file:
    url = photo_server['upload_url']
    files = {
        'photo': file
    }

    response = requests.post(url, files=files)
    response.raise_for_status()

loaded_img = response.json()

payload = {
    'group_id': group_id,
    'server': loaded_img['server'],
    'photo': loaded_img['photo'],
    'hash': loaded_img['hash'],
    'access_token': access_token,
    'v': 5.131,
}

response = requests.post(URL_API_VK_SAVE_PHOTO, params=payload)
response.raise_for_status()

save_img = response.json()['response'][0]

attachments = 'photo{}_{}'.format(save_img['owner_id'], save_img['id'])
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
