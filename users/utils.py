import requests

def upload_to_imgbb(image_file):
    url = "https://api.imgbb.com/1/upload"
    api_key = "620b20cce0b56095360ae5f1c0d6d289"  # Замініть на ваш API ключ від imgbb
    files = {'image': image_file}

    response = requests.post(url, files=files, data={"key": api_key})

    if response.status_code == 200:
        data = response.json()
        return data["data"]["url"]  # Повертаємо URL завантаженого зображення
    else:
        raise Exception(f"Error uploading image: {response.status_code}")
