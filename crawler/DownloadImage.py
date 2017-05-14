import os
import Queue

import requests
import threading
from PIL import Image
import traceback

queue = Queue.Queue()
BASE_LOCATION = "/home/ubuntu/data/img"

with open('photos/photos.txt') as data_file:
    for line in data_file:
        rows = line.split(",")
        photo_id = int(rows[0].strip())
        link = rows[1].strip()
        # print photo_id
        queue.put((photo_id, link))


def create_folder_if_not_exist(file_name):
    dir = os.path.dirname(file_name)
    try:
        os.stat(dir)
    except:
        os.makedirs(dir)


def convert_to_jpeg(from_name, to_name):
    im = Image.open(from_name)
    im.save(to_name, "JPEG")


def download_img(url, location):
    if not os.path.isfile(location):
        r = requests.get(url, stream=True, timeout=10)
        create_folder_if_not_exist(location)
        with open(location, "wb") as code:
            code.write(r.content)


def download():
    while not queue.empty():
        try:
            photo_id, link = queue.get()

            if ".png" in link:
                name = BASE_LOCATION + "/" + str(photo_id) + ".png"
            else:
                name = BASE_LOCATION + "/" + str(photo_id) + ".jpg"

            download_img(link, name)

            if ".png" in link:
                from_name = BASE_LOCATION + "/" + str(photo_id) + ".png"
                to_name = BASE_LOCATION + "/" + str(photo_id) + ".jpg"
                convert_to_jpeg(from_name, to_name)
            print photo_id
        except Exception, e:
            traceback.print_exc(e)


threads = []
for i in range(0, 20):
    t = threading.Thread(target=download)
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

# download_img("http://media1.modcloth.com/community_outfit_image/000/000/118/620/img_full_0b9891553f16.png",
#              "./000000021.png")
# convert_to_jpeg("000000021.png", "000000021.jpg")
