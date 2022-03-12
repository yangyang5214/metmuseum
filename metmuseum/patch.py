import os.path
import subprocess

from loading import *


def run_system_cmd(cmd):
    out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
    return out.decode('utf-8').strip()




def main():
    all_ids = get_all_ids()

    for object_id in all_ids:
        object_dir = os.path.join(target_dir, object_id)
        if os.path.exists(os.path.join(object_dir, 'flag')):
            with open(os.path.join(object_dir, "{}.json".format(object_id))) as f:
                data = json.load(f)
                images = [data.get('primaryImage')] + data.get('additionalImages', [])

                now_size = int(run_system_cmd("ls -f {} | grep *jpg | wc -l ".format(object_dir)))
                expect_size = len(images)
                if now_size != expect_size:
                    print("now: {}, expect: {}".format(now_size, expect_size))
                    print(object_id)


if __name__ == '__main__':
    main()
