import os.path
import subprocess

from loading import *

result_dir = "/home/pi/sda1/metmuseum/result"


def run_system_cmd(cmd):
    out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
    return out.decode('utf-8').strip()


def main():
    for keyword in os.listdir(keyword_ids_dir):
        keyword_file = os.path.join(keyword_ids_dir, keyword)
        result_keyword_dir = os.path.join(result_dir, keyword)
        if not os.path.exists(result_keyword_dir):
            run_system_cmd("mkdir -p {}".format(result_keyword_dir))

        print("keyword_file: {}".format(keyword_file))
        with open(keyword_file, 'r') as f:
            data = json.load(f)
            if not data:
                continue
            for object_id in data:
                object_dir = os.path.join(target_dir, object_id)
                object_file = os.path.join(object_dir, "{}.json".format(object_id))
                if not os.path.exists(object_file):
                    continue
                with open(object_file, 'r') as obj_f:
                    data = json.load(obj_f)
                    images = [data.get('primaryImage')] + data.get('additionalImages', [])
                    now_size = int(run_system_cmd("ls -f {} | grep jpg | wc -l ".format(object_dir)))
                    expect_size = len(images)
                    if now_size == expect_size:
                        cmd = "tar -P -cvf {}.tar.gz {}".format(os.path.join(result_keyword_dir, object_id), object_dir)
                        print(cmd)
                        run_system_cmd(cmd)
                    else:
                        print('😭 now_size: {}, expect_size: {}, {}'.format(now_size, expect_size, object_file))


if __name__ == '__main__':
    main()
