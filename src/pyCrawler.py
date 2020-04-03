# -*- coding: utf8 -*-

import json, sys, os, datefinder, logging, logging.handlers
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

chromeDriverFile = ""
crawlingDate = ""
devEnvironment = ""

# URL wait time
urlTimeWait = 3

# Web driver options
option = webdriver.ChromeOptions()
option.headless = True;
option.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")


def getDictionary( key, value ):
    jsonDict = {}
    jsonDict[key] = value
    return jsonDict

# Do crawling
#   requestList = [ { "subject" : subject, "urls" : [ "urls", "xxx", ... ] } ]
#   result = [ { "subject": "", "crawlingDate": "", "contents": [ { "sourceURL": "", "headline": "", "context": "" }, { ...  }, ... ],
#              "subject": "", "crawlingDate": "", "contents": [ { "sourceURL": "", "headline": "", "context": "" }, { ...  }, ... ], ... } ]
def doCrawling(requestList):
    index = 0
    result = []
    for jsonList in requestList:
        contents = []
        for url in jsonList["urls"] :

            sourceURL = getDictionary("sourceURL", url)

            #logging.info("main() - Generate web driver instance")
            driver = getWebDriver(sourceURL["sourceURL"], urlTimeWait)

            headline = getDictionary("headline", driver.find_element_by_xpath('//*[@id="aNews_View"]/h2').text)
            context = getDictionary("context", driver.find_element_by_xpath('//*[@id="newsText"]').text)

            sourceURL.update(headline)
            sourceURL.update(context)

            contents.append(sourceURL)
            driver.close()
            driver.quit()

        subject = getDictionary("subject", jsonList["subject"])
        date = getDictionary("crawlingDate", crawlingDate)
        data = getDictionary("contents", contents)

        subject.update(date)
        subject.update(data)

        result.append(subject)
        logging.info("doCrawling() - result[" + str(index) + "]: " + str(subject))
        index += 1

    return result

# Contents main page open
def getContentsUrls(url):

    try:
        driver = getWebDriver(url, urlTimeWait)
        contents_list = driver.find_element_by_xpath('//*[@id="aNews_List"]/ul')
        contents = contents_list.find_elements_by_tag_name('li')

        logging.info("getContentsUrls() - url :: " + url )

        urlList = []
        for content in contents:
            newsDate = str(list(datefinder.find_dates(str(content.find_element_by_xpath('//a/div[@class="aNews_date"]').text)))[0]).split()[0]
            if newsDate == crawlingDate:
                urlList.append(content.find_element_by_css_selector('a').get_attribute('href'))
        driver.close()
        driver.quit()
    except NoSuchElementException:
        logging.WARNING("Element exception  ::  " + url)

    return urlList

# 크롤링 타겟 설정
def makeRequest(targetCategoriesFile, targetURLPrefix, targetURLMain):
    # Target category loading
    targetMainPageList = []

    with open(targetCategoriesFile, 'r') as target:
        categories = json.load(target)

    # 카테고리 설정된 크롤링 대상 카테고리 페이지 로딩
    logging.info("makeRequest() - Do make crawling target page")
    for categories in categories["Categories"]:
        if categories["target"] == "enabled":
            # 카테고리별 메인 페이지
            categoryMainUrl = targetURLPrefix + targetURLMain + str(categories["id"])

            # targetMainPage setting
            dictSubject = getDictionary("subject", categories["subject"])
            dictUrls = getDictionary("urls", getContentsUrls(categoryMainUrl))

            dictSubject.update(dictUrls)
            targetMainPageList.append(dictSubject)

            logging.info("makeRequest() - crawling target address :: " + str(dictSubject))

    return targetMainPageList

# 웹 드라이버 셋팅
def getWebDriver(url, timeWait):

    driver = webdriver.Chrome(chromeDriverFile, options=option)

    # Web driver open
    logging.info("getWebDriver() - open url :: " + url)
    driver.get(url)
    driver.implicitly_wait(timeWait)

    return driver

# Log setting
def setLoggingConsole():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

def setLoggingFile(fileName):
    logging.basicConfig(filename=fileName, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

# main function
if __name__ == "__main__":

    # Program argument setting
    #   argument :: dev environment, crawling - date
    if len(sys.argv) < 3:
        logging.error("argument error")
        logging.error("  allowd argument :: (SERVER) (DATE) [LOG_FILE]")
        logging.error("                     (LOCAL | DEV | TEST) (yyyy-mm-dd) [crawling.yyyymmdd.log] ")
        exit()
    elif len(sys.argv) == 3:
        setLoggingConsole()
    elif len(sys.argv) == 4:
        setLoggingFile(sys.argv[3])

    devEnvironment = sys.argv[1]
    crawlingDate = sys.argv[2]

    # 환경 설정 파일 로딩
    logging.info("main() - Load config file")
    with open( os.path.dirname(os.path.realpath(__file__)) + '/config/config.json', 'r') as configFile:
        config = json.load(configFile)

    # Chrome driver file path
    chromeDriverFile = config[devEnvironment]["ProjectHome"] + config["DEFAULT"]["ResourcePath"] + \
                       config[devEnvironment]["WebDriverPath"] + config["DEFAULT"]["WebDriver"]

    # Crawling target site
    targetURLPrefix = config["DEFAULT"]["TargetUrlPrefix"]
    targetURLMain = config["DEFAULT"]["TargetUrlMain"]

    # Crawling target category resource file
    targetCategoriesFile = config[devEnvironment]["ProjectHome"] + config["DEFAULT"]["ResourcePath"] + \
                         config["DEFAULT"]["ResourceFile"]

    # Make request page
    logging.info("main() - Make request pages")
    requestPages = makeRequest(targetCategoriesFile, targetURLPrefix, targetURLMain)

    # crawling
    # 특수 문자 예외 처리 필요 --> ', ", /, `, {, }, [, ] 등 json에서 허용되지 않는 문자 제거
    logging.info("main() - Start to do crawling")
    resultList = doCrawling(requestPages)

    # file writing
    logging.info("main() - File writing")
    fileNamePrefix = config[devEnvironment]["ProjectHome"] + config["DEFAULT"]["CrawledDataPath"] + \
                     config["DEFAULT"]["CrawledDataFile"]

    for result in resultList:
        try:

            fileName = fileNamePrefix \
                .replace('%date', result['crawlingDate'])\
                .replace('%subject', result['subject'].replace('/', ' and '))\

            fw = open( fileName, 'w')
            fw.write( json.dumps(result, sort_keys=True, indent=4) )
            fw.close()
        except OSError:
            logging.error("File write path error :: " + fileName)
            break

    # File close
    logging.info("main() - File closing")
    configFile.close()