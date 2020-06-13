# NLP Analyzer using NLTK
# -*- coding: utf8 -*-
import sys, logging, glob, tqdm
import pyUtilsClass, pyNLPClass

def setResult(result, arrayData):
    for word in arrayData:
        result.append(word)

if __name__ == '__main__':

    if len(sys.argv) < 3:
        logging.error("Argument error")
        logging.error("  Allowd argument :: (SERVER) (DATE)")
        logging.error("       SERVER: LOCAL | DEV | TEST")
        logging.error("       DATE: yyyy-MM-DD  ex> 2020-04-07")
        exit()

    sysEnv = sys.argv[1]
    date = sys.argv[2]

    utils = pyUtilsClass.Utils()
    NLTKAnalyzer = pyNLPClass.NLPAnalyzer()
    pyUtilsClass.setLogging2Console()

    # Config file open
    config = utils.readJsonFile(utils.getLocalPath() + '/../config/config.json')

    NLTKAnalyzer.setLogging(logging)
    NLTKAnalyzer.setNLTKPath( config[sysEnv]["NLTKPath"])

    # glob.glob(path) --> file list :: 날짜 기준 파일 리스트 모두 가져오기로 변환
    logging.info("main() - Load analysis target file list using glob")
    rawTextFileList = glob.glob(utils.getLocalPath() + "/.." + str(config["DEFAULT"]["NLPAnalysis"]["Source"]).replace("%date", sys.argv[2]) + '/*')

    logging.info("main() - Text analysis")
    for rawTextFile in rawTextFileList:
        logging.info("main() -   %s file" % rawTextFile)
        jsonRawData = utils.readJsonFile(rawTextFile)

        jsonResult = {}
        jsonResult['subject'] = jsonRawData['subject']
        jsonResult['crawlingDate'] = jsonRawData['crawlingDate']
        jsonResult['headline'] = []
        jsonResult['context'] = []

        for contents in tqdm.tqdm(jsonRawData["contents"]):
            headline = str(contents["headline"]).replace('\n', ". ")
            context = (str(contents["context"]).replace(".\n", ". ")).replace("\n", "")

            setResult(jsonResult['headline'], NLTKAnalyzer.doMorphemeAnalysis(headline))
            setResult(jsonResult['context'], NLTKAnalyzer.doMorphemeAnalysis(context))

        if jsonResult['headline'] is not None:
            utils.writeJsonFile(jsonResult, rawTextFile.replace("crawl", "NLP"))

    logging.info("main() - Done")