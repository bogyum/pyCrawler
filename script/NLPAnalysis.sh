#!/bin/bash

if [ $# -ne 2 ]; then
   echo "Usage: $0 [Server] [DATE like YYYY-MM-DD]"
   exit -1
fi

Server=$1
Date=$2

#Local(Mac) path
NLPHome='/home/student/work/pyTrendyWord_DataGenerator'

#Windows path
#CrawlingHome='/c/work/pyTrendyWord_DataGenerator'
NLPCode='pyMorphemeAnalyzer.py'

#Date=$(date '+%Y-%m-%d' -d '1 day ago')
if [ ! -d "${NLPHome}/log" ]; then
	mkdir -p ${NLPHome}/log
fi

if [ ! -d "${NLPHome}/result/NLP/${Date}" ]; then
	mkdir -p ${NLPHome}/result/NLP/${Date}
fi

python3 ${NLPHome}/src/${NLPCode} ${Server} ${Date}

