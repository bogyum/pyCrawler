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
CrawlingHome='/Users/jarvis/work/pyCrawler'
CrawlingCode='pyCrawler.py'

#Date=$(date '+%Y-%m-%d' -d '1 day ago')
if [ ! -d "${CrawlingHome}/log" ]; then
	mkdir ${CrawlingHome}/log
fi

Log="${CrawlingHome}/log/$Date.pyCrawler.log"

if [ ! -d "${CrawlingHome}/result/${Date}" ]; then
	mkdir ${CrawlingHome}/result/${Date}
fi

echo "ServerName=${ServerName}"
echo "Date=${Date}"

python3 ${CrawlingHome}/src/${CrawlingCode} ${ServerName} ${Date}

