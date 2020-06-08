# -*- coding: utf8 -*-
import json, sys, datefinder, logging
from selenium.common.exceptions import NoSuchElementException
import utilsClass, crawlerClass

utils = utilsClass.Utils()
urlTimeWait = 3

# Do crawling
#   requestList = [ { "subject" : subject, "urls" : [ "urls", "xxx", ... ] } ]
#   result = [ { "subject": "", "crawlingDate": "", "contents": [ { "sourceURL": "", "headline": "", "context": "" }, { ...  }, ... ],
#              "subject": "", "crawlingDate": "", "contents": [ { "sourceURL": "", "headline": "", "context": "" }, { ...  }, ... ], ... } ]
def doCrawling(requestList, crawler):

    result = []
    for jsonList in requestList:
        contents = []

        logging.info("doCrawling() - Crawling target subject :: " + jsonList["subject"])
        for url in jsonList["urls"] :

            sourceURL = utils.getDictionary("sourceURL", url)
            driver = crawler.getWebDriver(sourceURL["sourceURL"])

            headline = utils.getDictionary("headline", driver.find_element_by_xpath('//*[@id="aNews_View"]/h2').text)
            context = utils.getDictionary("context", driver.find_element_by_xpath('//*[@id="newsText"]').text)

            sourceURL.update(headline)
            sourceURL.update(context)

            contents.append(sourceURL)
            logging.info("doCrawling() - Crawling done. URL - " + str(sourceURL["sourceURL"]))

        subject = utils.getDictionary("subject", jsonList["subject"])
        date = utils.getDictionary("crawlingDate", crawlingDate)
        data = utils.getDictionary("contents", contents)

        subject.update(date)
        subject.update(data)

        result.append(subject)
    return result

# Contents main page open
def getContentsUrls(url, crawler):

    try:
        driver = crawler.getWebDriver(url)
        contents = driver.find_element_by_xpath('//*[@id="aNews_List"]/ul').find_elements_by_tag_name('li')

        logging.info("getContentsUrls() - url :: " + url )

        urlList = []
        for content in contents:
            newsDate = str(list(datefinder.find_dates(str(content.find_element_by_xpath('//a/div[@class="aNews_date"]').text)))[0]).split()[0]
            if newsDate == crawlingDate:
                urlList.append(content.find_element_by_css_selector('a').get_attribute('href'))
    except NoSuchElementException:
        logging.WARNING("Element exception  ::  " + url)

    return urlList

# 크롤링 타겟 설정
def makeRequest(targetCategoriesFile, targetURLPrefix, targetURLMain, crawler):
    # Target category loading
    targetMainPageList = []
    categories = utils.readJsonFile(targetCategoriesFile)

    # 카테고리 설정된 크롤링 대상 카테고리 페이지 로딩
    logging.info("makeRequest() - Do make crawling target page")
    for categories in categories["Categories"]:
        if categories["target"] == "enabled":
            # 카테고리별 메인 페이지
            categoryMainUrl = targetURLPrefix + targetURLMain + str(categories["id"])

            # targetMainPage setting
            dictSubject = utils.getDictionary("subject", categories["subject"])
            dictUrls = utils.getDictionary("urls", getContentsUrls(categoryMainUrl, crawler))

            dictSubject.update(dictUrls)
            targetMainPageList.append(dictSubject)

            logging.info("makeRequest() - crawling target address :: " + str(dictSubject))
    return targetMainPageList

# main function
# noinspection PyInterpreter
if __name__ == "__main__":

    # Program argument setting
    #   argument :: dev environment, crawling - date
    if len(sys.argv) < 3:
        logging.error("argument error")
        logging.error("  allowd argument :: (SERVER) (DATE) [LOG_FILE]")
        logging.error("                     (LOCAL | DEV | TEST) (yyyy-mm-dd) [crawling.yyyymmdd.log] ")
        exit()
    elif len(sys.argv) == 3:
        utilsClass.setLogging2Console()
    elif len(sys.argv) == 4:
        utilsClass.setLogging2File(sys.argv[3])

    runEnvironment = sys.argv[1]
    crawlingDate = sys.argv[2]

    # 환경 설정 파일 로딩
    logging.info("main() - Load config file")
    config = utils.readJsonFile( utils.getLocalPath() + '/../config/config.json' )

    # Chrome driver file path
    chromeDriverFile = utils.getLocalPath() + '/..' \ 
                       + config["DEFAULT"]["ResourcePath"] \
                       + (utils.getPlatform() == 'Darwin' ? '/mac_driver' : '/ubuntu_driver') \
                       + '/chromedriver'

    # Crawling target site
    targetURLPrefix = config["DEFAULT"]["Crawling"]["TargetUrlPrefix"]
    targetURLMain = config["DEFAULT"]["Crawling"]["TargetUrlMain"]

    # Crawling target category resource file
    targetCategoriesFile = utils.getLocalPath() \
                          + config["DEFAULT"]["ResourcePath"] + \
                          + config["DEFAULT"]["Crawling"]["ResourceFile"]

    # Crawler Object Generation
    crawler = crawlerClass.Crawler(chromeDriverFile)
    crawler.setURLTimeWait(urlTimeWait)

    # Make request page
    logging.info("main() - Make request pages")
    requestPages = makeRequest(targetCategoriesFile, targetURLPrefix, targetURLMain, crawler)

    # Crawling
    # 특수 문자 예외 처리 필요 --> ', ", /, `, {, }, [, ] 등 json에서 허용되지 않는 문자 제거
    logging.info("main() - Start to do crawling")
    resultList = doCrawling(requestPages, crawler)

    # Kill crawler driver
    crawler.driver.close()
    crawler.driver.quit()

    # file writing
    logging.info("main() - File writing")
    fileNamePrefix = utils.getLocalPath() \
                     + config["DEFAULT"]["Crawling"]["CrawledDataPath"] \
                     + config["DEFAULT"]["Crawling"]["CrawledDataFile"]

    for result in resultList:
        fileName = fileNamePrefix\
            .replace('%date', result['crawlingDate'])\
            .replace('%subject', result['subject'].replace('/', ' and '))
        utils.writeJsonFile(result, fileName)

    # File close
    logging.info("main() - File closing and done")
