import json
import sys
import datefinder
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

chromeDriverFile = ""
crawlingDate = ""
devEnvironment = ""

def getDictionary( key, value ):
    jsonDict = {}
    jsonDict[key] = value
    return jsonDict

# Do crawling
#   requestList = [ { "subject" : subject, "urls" : [ "urls", "xxx", ... ] } ]
#   result = [ { "subject": "", "crawlingDate": "", "contents": [ { "sourceURL": "", "headline": "", "context": "" }, { ...  }, ... ],
#              "subject": "", "crawlingDate": "", "contents": [ { "sourceURL": "", "headline": "", "context": "" }, { ...  }, ... ], ... } ]
def doCrawling(driver, requestList):
    index = 0
    result = []
    for jsonList in requestList:
        contents = []
        for url in jsonList["urls"] :
            driver.get(url)
            driver.implicitly_wait(3)

            sourceURL = getDictionary("sourceURL", url)
            headline = getDictionary("headline", driver.find_element_by_xpath('//*[@id="aNews_View"]/h2').text)
            context = getDictionary("context", driver.find_element_by_xpath('//*[@id="newsText"]').text)

            sourceURL.update(headline)
            sourceURL.update(context)

            contents.append(sourceURL)

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
def getContentsUrls(driver, url):

    try:
        driver.get(url)
        driver.implicitly_wait(3)

        contents_list = driver.find_element_by_xpath('//*[@id="aNews_List"]/ul')
        contents = contents_list.find_elements_by_tag_name('li')

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
def makeRequest(driver, targetCategoriesFile, targetURLPrefix, targetURLMain):
    # Target category loading
    targetMainPageList = []

    with open(targetCategoriesFile, 'r') as target:
        categories = json.load(target)

    # 카테고리 설정된 크롤링 대상 카테고리 페이지 로딩
    logging.info("makeRequest() - Do make crawling target page")
    for categories in categories["Categories"]:
        if categories["target"] == "enabled":
            # 카테고리별 메인 페이지
            categoryMainUrl = targetURLPrefix + "/" + targetURLMain + str(categories["id"])

            # targetMainPage setting
            dictSubject = getDictionary("subject", categories["subject"])
            dictUrls = getDictionary("urls", getContentsUrls(driver, categoryMainUrl))

            dictSubject.update(dictUrls)
            targetMainPageList.append(dictSubject)

            logging.info("makeRequest() - crawling target address :: " + str(dictSubject))

    return targetMainPageList

# 웹 드라이버 셋팅
def getWebDriver():
    option = webdriver.ChromeOptions()
    option.headless = True;
    option.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(chromeDriverFile, options=option)
    return driver

# Log setting
def setLogging():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

# main function
if __name__ == "__main__":

    setLogging()

    # Program argument setting
    #   argument :: dev environment, crawling - date
    if len(sys.argv) < 3:
        logging.error("argument error")
        logging.error("  allowd argument :: (SERVER) (DATE) [LOG_FILE]")
        logging.error("                     (LOCAL | DEV | TEST) (yyyy-mm-dd) [crawling.yyyymmdd.log] ")
        exit()
    elif len(sys.argv) == 4:
        logging.basicConfig(filename=sys.argv[3])

    devEnvironment = sys.argv[1]
    crawlingDate = sys.argv[2]

    # 환경 설정 파일 로딩
    logging.info("main() - Load config file")
    with open('./config/config.json', 'r') as configFile:
        config = json.load(configFile)

    # Chrome driver file path
    chromeDriverFile = config[devEnvironment]["ChromeDriverPath"] + "/" + config["DEFAULT"]["ChromeDriver"]
    # Crawling target site
    targetURLPrefix = config["DEFAULT"]["TargetUrlPrefix"]
    targetURLMain = config["DEFAULT"]["TargetUrlMain"]
    # Crawling target category resource file
    targetCategoriesFile = config[devEnvironment]["ResourcePath"] + "/" + config["DEFAULT"]["ResourceFile"]

    # Web driver open
    logging.info("main() - Generate web driver instance")
    driver = getWebDriver()

    # Make request page
    logging.info("main() - Make request pages")
    requestPages = makeRequest(driver, targetCategoriesFile, targetURLPrefix, targetURLMain)

    # crawling
    # 특수 문자 예외 처리 필요 --> ', ", /, `, {, }, [, ] 등 json에서 허용되지 않는 문자 제거
    logging.info("main() - Start to do crawling")
    resultList = doCrawling(driver, requestPages)

    # file writing
    logging.info("main() - File writing")
    for result in resultList:
        try:
            fileName = str(config["DEFAULT"]["CrawledDataFile"]).replace('%subject', result['subject']).replace('/', ' and ')
            fw = open( str(config[devEnvironment]["CrawledDataPath"]).replace('%date', result['crawlingDate']) + "/" + fileName, 'w')
            fw.write( json.dumps(result) )
            fw.close()
        except OSError:
            logging.error("File write path error :: " + str(config[devEnvironment]["CrawledDataPath"]).replace('%date', result['crawlingDate']) + "/" + fileName)
            break

    # File close
    logging.info("main() - File closing")
    configFile.close()