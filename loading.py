"""
merge
"""

import json
import os

keyword_ids_dir = "keyword_ids"
target_dir = "/home/pi/sda1/metmuseum/objects"


def get_all_ids():
    all_ids = set()
    for keyword in os.listdir(keyword_ids_dir):
        keyword_file = os.path.join(keyword_ids_dir, keyword)
        with open(keyword_file, 'r') as f:
            data = json.load(f)
            if not data:
                continue
            all_ids = all_ids.union(set(data))
    return all_ids


def main():
    all_ids = get_all_ids()

    flag = 0

    for object_id in all_ids:
        if os.path.exists(os.path.join(target_dir, object_id)):
            flag += 1

    flag = flag * 100

    print("loading {} %".format(flag // len(all_ids)))


if __name__ == '__main__':
    main()
