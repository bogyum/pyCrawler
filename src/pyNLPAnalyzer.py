# NLP Analyzer using NLTK
# -*- coding: utf8 -*-
import sys, os, nltk, numpy
import common

# NLP analysis using nltk
#    Needs :: word, pos-tag, count(total, subject)

def analyze(jsonRawData):
    print("analyze")


if __name__ == '__main__':

    if len(sys.argv) < 4:
        common.logging.error("Argument error")
        common.logging.error("  Allowd argument :: (SERVER) (DATE) (RAWDATAFILENAME) (LOGFILE)")
        common.logging.error("       SERVER: LOCAL | DEV | TEST")
        common.logging.error("       DATE: yyyy-MM-DD  ex> 2020-04-07")
        common.logging.error("       RAWDATAFILENAME: Raw data file name  ex> Economy_news.arirang.json")
        exit()
    elif len(sys.argv) == 3:
        common.setLoggingConsole()
    else :
        common.setLoggingFile(sys.argv[3])

    # Config file open
    common.logging.info("main() - Load config file")
    config = common.jsonFileOpen(os.path.dirname(os.path.realpath(__file__)) + './config/config.json')

    # Raw data file open
    common.logging.info("main() - Json file open(analysis target) :: " + sys.argv[3])
    jsonRawData = common.jsonFileOpen(str(config[sys.argv[1]]["RawData"]).replace('%date', sys.argv[2]) + '/' + sys.argv[3])

    # NLTK analysis
    common.logging.info("main() - Text analysis")
    result = analyze(jsonRawData)

    # File output
    common.logging.info("main() - File write")
    common.writeJsonFile(result, str(config["DEFAULT"]["NLPOutput"]).replace('%date', sys.argv[2]).replace('%subject', sys.argv[3]))
