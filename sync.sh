#!/bin/bash

set -ex

base_dir='/Users/beer/beer/metmuseum'

rsync -avzP $base_dir/* pi:/home/pi/metmuseum --exclude-from="$base_dir/exclude.list"