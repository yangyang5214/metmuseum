#!/bin/bash

set -ex

base_dir='/Users/beer/beer/metmuseum'

rsync -avzP $base_dir/* hdd:/home/zhanglong/code --exclude-from="$base_dir/exclude.list"