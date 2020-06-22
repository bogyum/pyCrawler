#!/bin/bash

if [ $# -ne 1 ]; then
   echo "Usage: $0 [DATE like YYYY-MM-DD]"
   exit -1
fi

Date=$1

#DEV path
CrawlingHome='/home/student/work/pyTrendyWord_DataGenerator'

#Windows path
CrawlingCode='pyCrawling.py'

#Date=$(date '+%Y-%m-%d' -d '1 day ago')
if [ ! -d "${CrawlingHome}/log" ]; then
	mkdir -p ${CrawlingHome}/log
fi

if [ ! -d "${CrawlingHome}/result/crawl/${Date}" ]; then
	mkdir -p ${CrawlingHome}/result/crawl/${Date}
fi

python3 ${CrawlingHome}/src/${CrawlingCode} ${Date}