# -*- coding: utf8 -*-

import sys, logging, json, re, tqdm
import pyUtilsClass, pyCrawlerClass, pyDAOClass
from selenium.common.exceptions import NoSuchElementException

urlTimeWait = 3
dao = pyDAOClass.DAO()

def setDBConnection(dbConfig):
    dao.setClient(dbConfig["host"], dbConfig["port"], dbConfig["id"], dbConfig["pw"])
    dao.setDB(dbConfig["database"])
    return dao

# Dictionary 에서 soundLink == "None" 인 단어리스트를 가져온다.
def getTargetWord4Crawling(dbConfig):

    logging.info("getWordList() - Generate crawling target word list")

    dao.setCollection(dbConfig["collections"]["worddict"])
    wordList = dao.selectMany({"info.soundLink": "None"}, {"_id": 0})

    return wordList

def getCrawling(crawler, url, wordInfo):

    try:
        driver = crawler.getWebDriver(url + wordInfo["word"])
        # 의미 정보
        # bugfix/WDC001-MeanParsing
        soundLink = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div[1]/div[2]/span[1]/a').get_attribute('data-url')
        wordInfo['info']['soundLink'] = soundLink

        # 영영사전의 뜻풀이
        try:
            englishDictMeans = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[3]/div[2]/div[1]/ul/li/span').text
            wordInfo['info']['englishDic'] = englishDictMeans
        except NoSuchElementException:
            wordInfo['info']['englishDic'] = 'None'

    except NoSuchElementException:
        logging.info('%s 단어가 사전에 없습니다.' % url)

    return wordInfo

def setWordDictionary(wordList, collectionName, crawler, targetUrl):
    dao.setCollection(collectionName)

    logging.info("setWordDictionary() - Crawling and save to TrendWord.WordDictioanry")
    for wordinfo in tqdm.tqdm(wordList):
        info = getCrawling(crawler, targetUrl, wordinfo)
        if info is not None:
            dao.update({"word": wordinfo["word"]}, {"$set": info})
    dao.setClose()

if __name__=="__main__":

    logging.info("main() - Load config file")

    if len(sys.argv) < 3:
        logging.error("Argument error")
        logging.error("    Allowed argument: [Server] [DB_CONFIG_FILE]")
        exit()

    utils = pyUtilsClass.Utils()
    config = utils.readJsonFile(utils.getLocalPath() + '/../config/config.json')
    dbConfig = utils.readJsonFile(utils.getLocalPath() + "/../config/" + sys.argv[2])

    # 몽고디비 셋팅(Word Dictionary)
    dao = setDBConnection(dbConfig[sys.argv[1]])

    # 크롤러 셋팅
    chromeDriverFile = utils.getLocalPath() + '/..' + config["DEFAULT"]["ResourcePath"] + \
                       config["DEFAULT"]["Crawling"]["ChromeDriver"] + "/" + utils.getPlatform()
    targetUrl = config["DEFAULT"]["CrawlingDict"]["TargetUrl4Sound"]
    crawler = pyCrawlerClass.Crawler(chromeDriverFile)
    crawler.setURLTimeWait(urlTimeWait)

    setWordDictionary(getTargetWord4Crawling(dbConfig[sys.argv[1]]), dbConfig[sys.argv[1]]["collections"]["worddict"], crawler, targetUrl)
    crawler.closeDriver()

