#!/bin/bash
WORK_DIR="/root/Github/ff_crawler/models/Issue4"
echo "Start Reddit dumper at `date +'%Y/%m/%d %H:%M:%S'`..."
cd "$WORK_DIR"
echo "WORK_DIR=`pwd`"
source env/bin/activate
python reddit_dumper.py
echo "Done at `date +'%Y/%m/%d %H:%M:%S'`!"
deactivate
