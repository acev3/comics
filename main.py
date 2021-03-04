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


def get_xckd_image(comics_id=1, correct_folder="images"):
    url = "http://xkcd.com/{}/info.0.json".format(comics_id)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    image_url = response.json()["img"]
    title = response.json()["title"]
    alt = response.json()["alt"]
    if not os.path.exists(correct_folder):
        os.mkdir(correct_folder)
    filepath = os.path.join(correct_folder, title)
    filename = save_image(image_url, filepath)
    return title, alt, filename


def get_upload_server(VK_ACCESS_TOKEN, VK_GROUP_ID, VK_API_VERSION,
                      method_name="photos.getWallUploadServer"
                      ):
    params = "group_id={}".format(VK_GROUP_ID)
    access_token = VK_ACCESS_TOKEN
    url = "https://api.vk.com/method/{}?{}&access_token={}&v={}"\
        .format(method_name,
                params,
                access_token,
                VK_API_VERSION
                )
    response = requests.get(url, verify=False)
    response.raise_for_status()
    upload_url = response.json()["response"]["upload_url"]
    return upload_url


def upload_to_server(VK_ACCESS_TOKEN, VK_GROUP_ID, VK_API_VERSION, filename):
    upload_url = get_upload_server(VK_ACCESS_TOKEN,
                                   VK_GROUP_ID, VK_API_VERSION
                                   )
    with open(filename, "rb") as file:

        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    server = response.json()["server"]
    photo = response.json()["photo"]
    hash_answer = response.json()["hash"]
    return server, photo, hash_answer


def save_image_on_server(VK_ACCESS_TOKEN, VK_GROUP_ID, VK_API_VERSION,
                         filename, method_name="photos.saveWallPhoto"
                         ):
    server, photo, hash_answer = upload_to_server(VK_ACCESS_TOKEN, VK_GROUP_ID,
                                                  VK_API_VERSION, filename
                                                  )
    params = "group_id={}&server={}&photo={}&hash={}"\
        .format(VK_GROUP_ID, server,
                photo, hash_answer
                )
    url = "https://api.vk.com/method/{}?{}&access_token={}&v={}"\
        .format(method_name,
                params,
                VK_ACCESS_TOKEN,
                VK_API_VERSION
                )
    response = requests.post(url, verify=False)
    response.raise_for_status()
    media_id = response.json()["response"][0]["id"]
    owner_id = response.json()["response"][0]["owner_id"]
    return media_id, owner_id


def publication_post(VK_ACCESS_TOKEN, VK_GROUP_ID, VK_API_VERSION,
                     message, filename, method_name="wall.post"
                     ):
    group_publication_tag = 1
    media_id, owner_id = save_image_on_server(VK_ACCESS_TOKEN, VK_GROUP_ID,
                                              VK_API_VERSION, filename
                                              )
    attachments = "photo{}_{}".format(owner_id, media_id)
    params = "owner_id=-{}&from_group={}&attachments={}&message={}"\
        .format(VK_GROUP_ID,
                group_publication_tag, attachments, message
                )
    url = "https://api.vk.com/method/{}?{}&access_token={}&v={}"\
        .format(method_name,
                params,
                VK_ACCESS_TOKEN,
                VK_API_VERSION
                )
    response = requests.post(url, verify=False)
    response.raise_for_status()


def main():
    load_dotenv()
    VK_ACCESS_TOKEN = os.environ["VK_ACCESS_TOKEN"]
    VK_GROUP_ID = os.environ["VK_GROUP_ID"]
    VK_API_VERSION = os.environ["VK_API_VERSION"]
    last_comics_number = get_last_comics_number()
    comics_id = random.randint(1, int(last_comics_number))
    title, alt, filename = get_xckd_image(comics_id=comics_id)
    message = title + alt
    publication_post(VK_ACCESS_TOKEN, VK_GROUP_ID, VK_API_VERSION,
                     message, filename
                     )
    os.remove(filename)

def get_last_comics_number(url="http://xkcd.com/info.0.json"):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    last_comics_number = response.json()['num']
    return last_comics_number



if __name__ == '__main__':
    main()




