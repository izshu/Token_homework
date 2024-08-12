import requests  # type: ignore
import json
import datetime


TOKEN_VK = "vk1.a.ACOs8jtn0qKzPhMR61ghQ3OrP8pFrZhHcEQdN5qmy6phd2OA0LIIzoHJG5hEqVxOeNDNq7YZB9yLNbaEyk7ZeJtSqQG3ZvxKnPJ4NQYZF0g_p1E-ccKwz40YORpnm5MNbERfjC3bitVHbkiRp7WXbrvZDLh1YxCpVxX1AjgO4JhRRs87hrlh9owFuHrUoN4PndJa16vQGO00Vb1cG4SWzw"
TOKEN_YX = ""


class VK:

    API_BASE_URL = "https://api.vk.com/method/"

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {"access_token": self.token, "v": "5.131"}

    def copy_photos_vk(self, count=5):
        params = self.get_common_params()
        params.update({"owner_id": self.user_id, "extended": 1, "photo_sizes": 1, "count": count})
        response = requests.get(f"{self.API_BASE_URL}photos.getAll?", params=params)
        data = response.json()

        if "error" in data:
            return f"Error: {data['error']['error_msg']}"

        photos = []
        for row in data["response"]["items"]:
            sizes = row["sizes"]
            max_size = max(sizes, key=lambda s: s["width"] * s["height"])
            photos.append(
                {
                    "url": max_size["url"],
                    "likes": row["likes"]["count"],
                    "date": datetime.datetime.fromtimestamp(row["date"]).strftime("%Y-%m-%d_%H-%M-%S"),
                }
            )
        return photos


class Yandex:

    API_BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, token):
        self.token = token

    def get_common_headers(self):
        return {"Authorization": f"OAuth {self.token}"}

    def create_folder(self, folder_name):
        headers = self.get_common_headers()
        params = {"path": folder_name}
        response = requests.put(f"{self.API_BASE_URL}", params=params, headers=headers)
        if response.status_code == 201:
            print(f"Folder '{folder_name}' created successfully")
        elif response.status_code == 409:
            print(f"Folder '{folder_name}' already exists")
        else:
            print(f"Error creating folder: {response.status_code}")
        return folder_name

    def upload_file(self, file_name, folder, file_url):
        headers = self.get_common_headers()
        params = {"path": f"disk:/{folder}/{file_name}", "url": file_url}
        response = requests.post(f"{self.API_BASE_URL}/upload", headers=headers, params=params)
        if response.status_code == 202:
            print(f"File '{file_name}' uploaded successfully to folder '{folder}'")
        else:
            print(f"Error uploading file '{file_name}': {response.status_code}")


def backup_photos(vk_client, ya_client, count=1):
    photos = vk_client.copy_photos_vk(count=count)
    folder_name = ya_client.create_folder("VK_Backup")

    photo_info_list = []

    for photo in photos:
        file_name = f"{photo['likes']}.jpg"
        if any(p["file_name"] == file_name for p in photo_info_list):
            file_name = f"{photo['likes']}_{photo['date']}.jpg"

        ya_client.upload_file(file_name, folder_name, photo["url"])
        photo_info_list.append({"file_name": file_name, "size": "z"})

    return photo_info_list


def save_backup_info(photo_info_list):
    with open("Token_homework/vk_photos_backup.json", "w") as f:
        json.dump(photo_info_list, f, ensure_ascii=False, indent=4)
    print("Backup completed and information saved to 'vk_photos_backup.json'")


def main():
    vk_client = VK(TOKEN_VK, )  # Первое токен, второе id странички в вк откуда будут копироваться фото.
    ya_client = Yandex(TOKEN_YX)  # Токен яндекс диска

    photo_info_list = backup_photos(
        vk_client, ya_client, count=1  # В count нужно ввести кол-во фото для загрузки на яндекс диск.
    )
    save_backup_info(photo_info_list)


if __name__ == "__main__":
    main()
