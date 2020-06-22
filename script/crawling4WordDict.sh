#!/bin/bash

if [ $# -ne 2 ]; then
   echo "Usage: $0 [Server] [DB_CONFIG_FILE]"
   exit -1
fi

Server=$1
DB=$2

HOME='/home/student/work/pyTrendyWord_DataGenerator'
CODE='pyCrawling.py'

python3 ${HOME}/src/${CODE} ${Server} ${DB}
