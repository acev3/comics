import requests
import os
import random
from dotenv import load_dotenv
from PIL import Image


def save_image(url, filepath):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(filepath, "wb") as file:
        file.write(response.content)
        image = Image.open(filepath)
        filename = "{}{}".format(filepath, ".jpg")
        image.save(filename, format="JPEG")
        os.remove(filepath)
    return filename


def get_xckd_image(comics_id=1, folder="comics"):
    url = "http://xkcd.com/{}/info.0.json".format(comics_id)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    decoded_response = response.json()
    image_url = decoded_response["img"]
    title = decoded_response["title"]
    author_comments = decoded_response["alt"]
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, title)
    return title, author_comments, image_url, filepath


def get_upload_server(vk_access_token, vk_group_id, vk_api_version,
                      method_name="photos.getWallUploadServer"
                      ):
    payload = {"group_id": vk_group_id,
               "access_token": vk_access_token,
               "v": vk_api_version
               }
    url = "https://api.vk.com/method/{}".format(method_name)
    response = requests.get(url, params=payload, verify=False)
    decoded_response = response.json()
    vk_api_raise_for_status(decoded_response)
    upload_url = decoded_response["response"]["upload_url"]
    return upload_url


def upload_to_server(filename, upload_url):
    with open(filename, "rb") as file:

        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files)
        decoded_response = response.json()
        vk_api_raise_for_status(decoded_response)
    server = decoded_response["server"]
    photo = decoded_response["photo"]
    hash_answer = decoded_response["hash"]
    return server, photo, hash_answer


def save_image_on_server(vk_access_token, vk_group_id, vk_api_version,
                         server, photo, hash_answer,
                         method_name="photos.saveWallPhoto"
                         ):
    payload = {"group_id": vk_group_id,
               "server": server,
               "photo": photo,
               "hash": hash_answer,
               "access_token": vk_access_token,
               "v": vk_api_version
               }
    url = "https://api.vk.com/method/{}".format(method_name)
    response = requests.post(url, params=payload, verify=False)
    decoded_response = response.json()
    vk_api_raise_for_status(decoded_response)
    media_id = decoded_response["response"][0]["id"]
    owner_id = decoded_response["response"][0]["owner_id"]
    return media_id, owner_id


def publication_post(vk_access_token, vk_group_id, vk_api_version,
                     message, media_id, owner_id, method_name="wall.post"
                     ):
    group_publication_tag = 1
    attachments = "photo{}_{}".format(owner_id, media_id)
    owner_id = "-{}".format(vk_group_id)
    payload = {"owner_id": owner_id,
               "from_group": group_publication_tag,
               "attachments": attachments,
               "message": message,
               "access_token": vk_access_token,
               "v": vk_api_version
               }
    url = "https://api.vk.com/method/{}".format(method_name)
    response = requests.post(url, params=payload, verify=False)
    decoded_response = response.json()
    vk_api_raise_for_status(decoded_response)


def get_last_comics_number(url="http://xkcd.com/info.0.json"):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    last_comics_number = response.json()['num']
    return last_comics_number


def vk_api_raise_for_status(decoded_response):
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])


def main():
    load_dotenv()
    vk_access_token = os.environ["VK_ACCESS_TOKEN"]
    vk_group_id = os.environ["VK_GROUP_ID"]
    vk_api_version = os.environ["VK_API_VERSION"]
    last_comics_number = get_last_comics_number()
    comics_id = random.randint(1, int(last_comics_number))
    title, author_comments, image_url, filepath = get_xckd_image(
            comics_id=comics_id)
    filename = save_image(image_url, filepath)
    message = "{}.{}".format(title, author_comments)
    try:
        upload_url = get_upload_server(vk_access_token, vk_group_id,
                                       vk_api_version
                                       )
        server, photo, hash_answer = upload_to_server(filename, upload_url)
        media_id, owner_id = save_image_on_server(vk_access_token,
                                                  vk_group_id, vk_api_version,
                                                  server, photo, hash_answer
                                                  )
        publication_post(vk_access_token, vk_group_id, vk_api_version,
                         message, media_id, owner_id
                         )
    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()




