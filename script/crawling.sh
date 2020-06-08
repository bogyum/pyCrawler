#!/bin/bash

if [ $# -ne 1 ]; then
   echo "Usage: $0 [DATE like YYYY-MM-DD]"
   exit -1
fi

Date=$1

#Local(Mac) path
CrawlingHome='/Users/jarvis/work/pyTrendyWord_DataGenerator'

#Windows path
#CrawlingHome='/c/work/pyTrendyWord_DataGenerator'
CrawlingCode='pyCrawling.py'

#Date=$(date '+%Y-%m-%d' -d '1 day ago')
if [ ! -d "${CrawlingHome}/log" ]; then
	mkdir -p ${CrawlingHome}/log
fi

Log="${CrawlingHome}/log/$Date.pyCrawler.log"

if [ ! -d "${CrawlingHome}/result/crawl/${Date}" ]; then
	mkdir -p ${CrawlingHome}/result/crawl/${Date}
fi

python ${CrawlingHome}/src/${CrawlingCode} ${Date}

