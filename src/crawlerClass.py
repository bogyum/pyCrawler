from selenium import webdriver

class Crawler:

    urlTimeWait = 3

    def __init__(self, chromeDriver):
        self.chromeDriver = chromeDriver

        option = webdriver.ChromeOptions()
        option.headless = True;
        option.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

        self.driver = webdriver.Chrome(self.chromeDriver, options = option)


    # 웹 드라이버 셋팅
    def getWebDriver(self, url):

        # Web driver open
        # logging.info("getWebDriver() - open url :: " + url)
        self.driver.get(url)
        self.driver.implicitly_wait(self.urlTimeWait)

        return self.driver

    def setURLTimeWait(self, urlTimeWait):
        self.urlTimeWait = urlTimeWait


