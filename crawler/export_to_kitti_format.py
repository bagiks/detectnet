import json
import os
import re
import threading
from subprocess import Popen
from PIL import Image

data = {}

lock = threading.Lock()

BASE_IMAGE_LOCATION = "/data/img"

BASE_FORMAT_LOCATION = "/data/export/kitti"


def create_folder_if_not_exist(file_name):
    lock.acquire()
    dir = os.path.dirname(file_name)
    try:
        os.stat(dir)
    except:
        os.makedirs(dir)
    lock.release()


def process_file(file_name, category, type, num):
    count = 0
    with open(file_name) as meta_file:
        meta_obj_list = json.load(meta_file)

        for meta_obj in meta_obj_list:
            if count >= num:
                break
            else:
                print count
            type = "val" if type == "test" else type
            try:
                photo_id = meta_obj["photo"]

                bbox = meta_obj["bbox"]
                width = bbox["width"]
                top = bbox["top"]
                left = bbox["left"]
                height = bbox["height"]

                output_data = "%s 0.0 0 0.0 %s %s %s %s 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n" % (
                    category, left, top, left + width, top + height)

                annotation_file = BASE_FORMAT_LOCATION + "/" + type + "/labels/" + str(photo_id) + ".txt"
                create_folder_if_not_exist(annotation_file)
                

                image_file = BASE_FORMAT_LOCATION + "/" + type + "/images/" + str(photo_id) + ".jpg"
                
                image = Image.open(BASE_IMAGE_LOCATION + "/" + str(photo_id) + ".jpg")
                
                if image.size[0] < 2000 and image.size[1] < 1000:
                    f = open(annotation_file, "a+")
                    f.write(output_data)
                    f.close()
                    create_folder_if_not_exist(image_file)
                    p = Popen(
                        ['cp', BASE_IMAGE_LOCATION + "/" + str(photo_id) + ".jpg", image_file])
                    p.wait()
                count += 1
            except Exception, e:
                import traceback

                traceback.print_exc(e)
#            count += 1


threads = []

train_num_per_cate = 1000
valid_num_per_cate = 100
test_num_per_cate = 100

configs = {"train": 1000, "test": 100}

for type, num in configs.iteritems():
    pattern = re.compile(type + "_pairs_(.*?)\.json")
    for (dirpath, dirnames, filenames) in os.walk("meta/json"):
        for filename in filenames:
            if pattern.match(filename):
                m = pattern.match(filename)
                category = m.group(1)
                print filename
                print category

                t = threading.Thread(target=process_file, args=("meta/json/" + filename, category, type, num))

                threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()
