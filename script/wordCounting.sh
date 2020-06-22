#!/bin/bash

if [ $# -ne 3 ]; then
   echo "Usage: $0 [Server] [DB_CONFIG_FILE] [DATE like YYYY-MM-DD]"
   exit -1
fi

Server=$1
DB_CONFIG_FILE=$2
Date=$3

#DEV path
HOME='/home/student/work/pyTrendyWord_DataGenerator'

#Windows path
#CrawlingHome='/c/work/pyTrendyWord_DataGenerator'
CODE='pyWordCount.py'

#Date=$(date '+%Y-%m-%d' -d '1 day ago')
if [ ! -d "${HOME}/log" ]; then
	mkdir -p ${HOME}/log
fi

python3 ${HOME}/src/${CODE} ${Server} ${Date} ${DB_CONFIG_FILE}