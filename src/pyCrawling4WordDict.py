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

# word count / word dictionary 두 컬렉션을 조인하여, word dictionary 에 등록되지 않은 단어 목록을 크롤링 대상으로 한다.
def getWordList(dbConfig):

    logging.info("getWordList() - Generate crawling target word list")

    wordList = set()
    dao.setCollection(dbConfig["collections"]["wordcount"])
    wordList4Count = dao.selectMany({}, {"word": 1, "_id": 0})
    for info in wordList4Count:
        wordList.add(info["word"])

    dictWordList = set()
    dao.setCollection(dbConfig["collections"]["worddict"])
    wordList4Dict = dao.selectMany({}, {"word": 1, "_id": 0})
    for info in wordList4Dict:
        if wordList.__contains__(info["word"]):
            wordList.remove(info["word"])

    return wordList

def getCrawling(crawler, url):

    result = {'meaning': {}, 'pronounce': '', 'soundLink': '', 'exampleText': '', 'exampleKoreanText': ''}
    try:
        driver = crawler.getWebDriver(url)
        # 의미 정보
        # bugfix/WDC001-MeanParsing
        meanList = driver.find_elements_by_xpath('//*[@id="searchPage_entry"]/div/div[1]/ul')
        for mean in meanList:
            meanItems = mean.find_elements_by_tag_name('li')
            for mean in meanItems:
                tagName = str(mean.find_element_by_tag_name("p").find_element_by_tag_name("span").text).strip()
                meanText = str(mean.find_element_by_tag_name("p").text).replace(tagName, '').replace('\n', ' ').strip()
                if tagName in result["meaning"]:
                    result["meaning"][tagName].append(meanText)
                else:
                    result["meaning"][tagName] = [meanText]

        # 발음 기호
        pronounce = driver.find_element_by_xpath('//*[@id="searchPage_entry"]/div/div[1]/div[1]/ul/li[1]/span[1]')
        result["pronounce"] = pronounce.text

        # 예제 문장
        exampleText = driver.find_element_by_xpath('//*[@id="searchPage_example"]/div/div[1]/div[1]/span[1]').text
        result["exampleText"] = exampleText

        # 예제 문장 해석
        exampleKoreanText = driver.find_element_by_xpath('//*[@id="searchPage_example"]/div/div[1]/div[2]/p').text
        result["exampleKoreanText"] = exampleKoreanText

        # 음성 정보
        # bugfix/WDC001-MeanParsing :: 네이버 사전에서의 음성정보는 음성을 클릭시마다 암호화 key(lsa) 값을 요구하므로, 크롤링하는 것이 의미가 없음. 즉, 음성 정보 클릭 시 마다 이벤트가 발생해서, 해당 정보를 가져오는 방식임.
        #  --> 이는 다음 사전을 크롤링하면 해결 가능함.
        #  -->  다음 사전에서 음성 링크만 가져오기 위해 필드만 생성한 뒤 'None' 정보 입력. 후에 이러한 단어만 모아서, 다음 사전에서 크롤링 하면 될 듯 함.
        result["soundLink"] = 'None'

    except NoSuchElementException:
        logging.info('%s 단어가 사전에 없습니다.' % url)
        result = None

    return result

def setWordDictionary(wordList, collectionName, crawler, targetUrl):
    dao.setCollection(collectionName)

    logging.info("setWordDictionary() - Crawling and save to TrendWord.WordDictioanry")
    for word in tqdm.tqdm(wordList):
        # 영문자가 포함되어 있을 경우에만..
        if re.search('[a-zA-Z]', word):
            info = getCrawling(crawler, targetUrl + word)
            if info is not None:
                dao.insert({"word": word, "info": info})
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
    targetUrl = config["DEFAULT"]["CrawlingDict"]["TargetUrl"]
    crawler = pyCrawlerClass.Crawler(chromeDriverFile)
    crawler.setURLTimeWait(urlTimeWait)

    setWordDictionary(getWordList(dbConfig[sys.argv[1]]), dbConfig[sys.argv[1]]["collections"]["worddict"], crawler, targetUrl)
    crawler.closeDriver()

