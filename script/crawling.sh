#!/bin/bash

CrawlingHome='/home/jarvis/work/pyCrawler'
CrawlingCode='pyCrawler.py'
ServerName='DEV'
Date=$(date '+%Y-%m-%d' -d '1 day ago')
Log="$CrawlingHome/log/$Date.pyCrawler.log"

if [ ! -d "$CrawlingHome/result/$Date" ]; then
	mkdir $CrawlingHome/result/$Date
fi

python3 $CrawlingHome/src/$CrawlingCode $ServerName $Date $Log

