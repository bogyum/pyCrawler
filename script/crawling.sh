#!/bin/bash

if [ $# -ne 2 ]; then
   echo "Usage: $0 [LOCAL|DEV|TEST] [DATE like YYYY-MM-DD]"
   exit -1
fi

ServerName=$1
Date=$2

#DEV server path
#CrawlingHome='/home/jarvis/work/pyCrawler' 

#Local server path
#CrawlingHome='/Users/jarvis/work/pyTrendyWord_DataGenerator'

#Windows path
CrawlingHome='/c/work/pyTrendyWord_DataGenerator'
CrawlingCode='pyCrawler.py'

#Date=$(date '+%Y-%m-%d' -d '1 day ago')
if [ ! -d "${CrawlingHome}/log" ]; then
	mkdir -p ${CrawlingHome}/log
fi

Log="${CrawlingHome}/log/$Date.pyCrawler.log"

if [ ! -d "${CrawlingHome}/result/crawl/${Date}" ]; then
	mkdir -p ${CrawlingHome}/result/crawl/${Date}
fi

echo "ServerName=${ServerName}"
echo "Date=${Date}"

python ${CrawlingHome}/src/${CrawlingCode} ${ServerName} ${Date}

