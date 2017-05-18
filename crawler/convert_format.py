import json
import os
import re
import threading
from subprocess import Popen
from PIL import Image

import sys, getopt

data = {}

lock = threading.Lock()

BASE_IMAGE_LOCATION = "/data/img"


def create_folder_if_not_exist(file_name):
    lock.acquire()
    dir = os.path.dirname(file_name)
    try:
        os.stat(dir)
    except:
        os.makedirs(dir)
    lock.release()


def process_kitti_file(file_name, category_id, category, type, num, OUTPUT_LOCATION):
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

                annotation_file = OUTPUT_LOCATION + "/" + type + "/labels/" + str(photo_id) + ".txt"
                create_folder_if_not_exist(annotation_file)

                image_file = OUTPUT_LOCATION + "/" + type + "/images/" + str(photo_id) + ".jpg"

                # image = Image.open(BASE_IMAGE_LOCATION + "/" + str(photo_id) + ".jpg")

                # if image.size[0] < 2000 and image.size[1] < 1000:
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


lock = threading.Lock()

def process_voc_file(file_name, category_id, category, type, num, OUTPUT_LOCATION):
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

                output_data = "%s %s %s %s %s\n" % (
                    category_id, left, top, width, height)

                annotation_file = OUTPUT_LOCATION + "/" + type + "/labels/" + str(photo_id) + ".txt"
                create_folder_if_not_exist(annotation_file)

                image_file = OUTPUT_LOCATION + "/" + type + "/images/" + str(photo_id) + ".jpg"

                # image = Image.open(BASE_IMAGE_LOCATION + "/" + str(photo_id) + ".jpg")

                # if image.size[0] < 2000 and image.size[1] < 1000:
                f = open(annotation_file, "a+")
                f.write(output_data)
                f.close()
                create_folder_if_not_exist(image_file)
                p = Popen(
                    ['cp', BASE_IMAGE_LOCATION + "/" + str(photo_id) + ".jpg", image_file])
                p.wait()

                lock.acquire()
                f = open(OUTPUT_LOCATION + "/" + type + ".txt", "a+")
                f.write(image_file)
                f.close()
                lock.release()

                count += 1
            except Exception, e:
                import traceback

                traceback.print_exc(e)


# count += 1

def main(train_num, test_num, OUTPUT_LOCATION, output_format_type):
    category_mapping = {}
    category_list = []
    category_id_idx = 0
    threads = []

    configs = {"train": train_num, "test": test_num}

    for data_type, num in configs.iteritems():
        pattern = re.compile(data_type + "_pairs_(.*?)\.json")
        for (dirpath, dirnames, filenames) in os.walk("meta/json"):
            for filename in filenames:
                if pattern.match(filename):
                    m = pattern.match(filename)
                    category = m.group(1)

                    if category in category_mapping:
                        category_id = category_mapping[category]
                    else:
                        category_mapping[category] = category_id_idx
                        category_id = category_id_idx
                        category_id_idx += 1

                    print filename
                    print category

                    category_list.append(category)

                    if output_format_type == "kitti":
                        t = threading.Thread(target=process_kitti_file,
                                             args=("meta/json/" + filename, category_id, category, data_type, num,
                                                   OUTPUT_LOCATION))
                        threads.append(t)
                    elif output_format_type == "voc":
                        t = threading.Thread(target=process_voc_file,
                                             args=("meta/json/" + filename, category_id, category, data_type, num,
                                                   OUTPUT_LOCATION))
                        threads.append(t)

    create_folder_if_not_exist(OUTPUT_LOCATION + "/" + "voc.names")
    f = open(OUTPUT_LOCATION + "/" + "voc.names", "w")

    for category in category_list:
        f.write(category + "\n")
    f.close()

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    BASE_FORMAT_LOCATION = "/data/export/kitti"

    argv = sys.argv[1:]

    print argv

    output_location = ''
    train_num = 0
    test_num = 0
    output_format_type = "kitti"

    try:
        opts, args = getopt.getopt(argv, "o:r:e:t:")
        print opts
    except getopt.GetoptError, e:
        import traceback

        traceback.print_exc(e)
        print 'test.py -o <outputfile> -r <train_num_per_cate> -e <test_num_per_cate> -t <output_type>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -o <outputfile> -r <train_num_per_cate> -e <test_num_per_cate> -t <output_type>'
            sys.exit()
        elif opt in ("-o", "--output_location"):
            output_location = arg
        elif opt in ("-r", "--train_num_per_cate"):
            train_num = int(arg)
        elif opt in ("-e", "--test_num_per_cate"):
            test_num = int(arg)
        elif opt in ("-t", "--output_type"):
            output_format_type = arg

    print 'output_location is "', output_location
    print 'train_num is "', train_num
    print 'test_num is "', test_num
    print 'output_format_type is "', output_format_type

    main(train_num, test_num, output_location, output_format_type)
