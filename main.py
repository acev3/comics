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
    decoded_response = response.json()
    image_url = decoded_response["img"]
    title = decoded_response["title"]
    alt = decoded_response["alt"]
    if not os.path.exists(correct_folder):
        os.mkdir(correct_folder)
    filepath = os.path.join(correct_folder, title)
    filename = save_image(image_url, filepath)
    return title, alt, filename


def get_upload_server(vk_access_token, vk_group_id, vk_api_version,
                      method_name="photos.getWallUploadServer"
                      ):
    params = "group_id={}".format(vk_group_id)
    access_token = vk_access_token
    url = "https://api.vk.com/method/{}?{}&access_token={}&v={}"\
        .format(method_name,
                params,
                access_token,
                vk_api_version
                )
    response = requests.get(url, verify=False)
    response.raise_for_status()
    upload_url = response.json()["response"]["upload_url"]
    return upload_url


def upload_to_server(vk_access_token, vk_group_id, vk_api_version, filename):
    upload_url = get_upload_server(vk_access_token,
                                   vk_group_id, vk_api_version
                                   )
    with open(filename, "rb") as file:

        files = {
            "photo": file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    decoded_response = response.json()
    server = decoded_response["server"]
    photo = decoded_response["photo"]
    hash_answer = decoded_response["hash"]
    return server, photo, hash_answer


def save_image_on_server(vk_access_token, vk_group_id, vk_api_version,
                         filename, method_name="photos.saveWallPhoto"
                         ):
    server, photo, hash_answer = upload_to_server(vk_access_token, vk_group_id,
                                                  vk_api_version, filename
                                                  )
    params = "group_id={}&server={}&photo={}&hash={}"\
        .format(vk_group_id, server,
                photo, hash_answer
                )
    url = "https://api.vk.com/method/{}?{}&access_token={}&v={}"\
        .format(method_name,
                params,
                vk_access_token,
                vk_api_version
                )
    response = requests.post(url, verify=False)
    response.raise_for_status()
    decoded_response = response.json()
    media_id = decoded_response["response"][0]["id"]
    owner_id = decoded_response["response"][0]["owner_id"]
    return media_id, owner_id


def publication_post(vk_access_token, vk_group_id, vk_api_version,
                     message, filename, method_name="wall.post"
                     ):
    group_publication_tag = 1
    media_id, owner_id = save_image_on_server(vk_access_token, vk_group_id,
                                              vk_api_version, filename
                                              )
    attachments = "photo{}_{}".format(owner_id, media_id)
    params = "owner_id=-{}&from_group={}&attachments={}&message={}"\
        .format(vk_group_id,
                group_publication_tag, attachments, message
                )
    url = "https://api.vk.com/method/{}?{}&access_token={}&v={}"\
        .format(method_name,
                params,
                vk_access_token,
                vk_api_version
                )
    response = requests.post(url, verify=False)
    response.raise_for_status()


def get_last_comics_number(url="http://xkcd.com/info.0.json"):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    last_comics_number = response.json()['num']
    return last_comics_number


def main():
    load_dotenv()
    vk_access_token = os.environ["VK_ACCESS_TOKEN"]
    vk_group_id = os.environ["VK_GROUP_ID"]
    vk_api_version = os.environ["VK_API_VERSION"]
    last_comics_number = get_last_comics_number()
    comics_id = random.randint(1, int(last_comics_number))
    title, alt, filename = get_xckd_image(comics_id=comics_id)
    message = title + alt
    publication_post(vk_access_token, vk_group_id, vk_api_version,
                     message, filename
                     )
    os.remove(filename)


if __name__ == '__main__':
    main()




