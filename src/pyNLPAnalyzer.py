# NLP Analyzer using NLTK
# -*- coding: utf8 -*-
import sys, os, logging, nltk, numpy
import utilsClass

utils = utilsClass.Utils()

# NLP analysis using nltk
#    Needs :: word, pos-tag, count(total, subject)

def morphemeAnalysis(text):
    sentToken = nltk.sent_tokenize(text, "english")
    for sent in sentToken:
        # 기사의 날짜와 리포터의 이름은 분석에서 제외
        if str(sent).find("Updated") > -1 or str(sent).find("Reporter") > -1:
            continue

        print("sentence :: " + sent)
        wordTokens = nltk.pos_tag(nltk.word_tokenize(sent))
        print(wordTokens)

if __name__ == '__main__':

    if len(sys.argv) < 3:
        logging.error("Argument error")
        logging.error("  Allowd argument :: (SERVER) (DATE) (RAWDATAFILENAME) (LOGFILE)")
        logging.error("       SERVER: LOCAL | DEV | TEST")
        logging.error("       DATE: yyyy-MM-DD  ex> 2020-04-07")
        logging.error("       RAWDATAFILENAME: Raw data file name  ex> Economy_news.arirang.json")
        exit()
    elif len(sys.argv) == 3:
        utilsClass.setLogging2Console()
    else :
        utilsClass.setLogging2File(sys.argv[3])

    # Config file open
    config = utils.readJsonFile(os.path.dirname(os.path.realpath(__file__)) + '/../config/config.json')


    # glob.glob(path) --> file list :: 날짜 기준 파일 리스트 모두 가져오기로 변환


    # Raw data file open
    #   :: 분석 대상 파일 리스트 가져오기
    rawDataPath = config[sys.argv[1]]["ProjectHome"] + str(config["DEFAULT"]["Crawling"]["CrawledDataPath"]).replace("%date", sys.argv[2])

    # Output file name
    outputFileName = config["DEFAULT"]["NLPAnalysis"]["AnalysisResultDataPath"] + config["DEFAULT"]["NLPAnalysis"]["MAResultDataFile"]

    # Set nltk path
    nltk.data.path.append(config[sys.argv[1]]["NLPAnalysis"]["NLTKPath"])

    fileList = utils.getDirFileList(rawDataPath)
    for file in fileList:
        jsonRawData = utils.readJsonFile(file)

        logging.info("main() - Analysis target :: " + file)
        if jsonRawData["contents"] == "[]":
            logging.info("main() -     No contents data")
            continue

        nlpResult = []
        for content in jsonRawData["contents"]:
            '''nlpResult.append(morphemeAnalysis(content["headline"]))
            nlpResult.append(morphemeAnalysis(content["context"]))'''
            morphemeAnalysis(content["headline"])
            morphemeAnalysis(content["context"])


        logging.info("main() -     Done")
        logging.info("main() - File output :: " + jsonRawData["subject"] + ", " + jsonRawData["crawlingDate"])

        '''utils.writeJsonFile(nlpResult, outputFileName
                            .replace("%date", sys.argv[2])
                            .replace("%subject", jsonRawData["subject"])
                            .replace("\\/", "_")) '''

    logging.info("main() - Analysis Done")
