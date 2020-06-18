# Word counting with pymongo
# -*- coding: utf8 -*-
import sys, logging, glob, json
import pyUtilsClass, pyDAOClass

dao = pyDAOClass.DAO()

def setDBConnection(dbConfig):
    dao.setClient(dbConfig["host"], dbConfig["port"], dbConfig["id"], dbConfig["pw"])
    dao.setDB(dbConfig["database"])
    dao.setCollection(dbConfig["collection"])
    return dao

def countWord(wordList):
    '''
        { "book": {
            "postag": ["", ...],
            "count": xxx
            },
          "have": {
            "postag": ["", ...],
            "count": xxx
            }, ...
        }
    '''

    wordCountList = {}
    for morph in wordList:
        word = str(morph)[:str(morph).rfind('/')]
        postag = str(morph)[str(morph).rfind('/')+1:]

        if wordCountList.get(word) != None:
            if not wordCountList[word]["postag"].__contains__(postag):
                wordCountList[word]["postag"].append(postag)
            wordCountList[word]["count"] += 1
        else:
            wordInfo = { "postag" : [postag], "count": 1}
            wordCountList[word] = wordInfo
    return wordCountList

def getCountArray(month, count):
    countArray = [0] * 12
    countArray[int(month) - 1] = count
    return countArray

def getPostagList(dbInfo, newData):
    for tag in newData:
        if not dbInfo.__contains__(tag):
            dbInfo.append(tag)
    return json.dumps(dbInfo)

def countWordinDB(date, subject, isHeader, countWordList):
    year = date.split('-')[0]
    month = date.split('-')[1]

    for wordInfo in countWordList:
        dbInfo = dao.select('{"word": "%s"}' % wordInfo)

        if dbInfo is not None:
            dbInfo["count"][str(year)][int(month)-1] += int(countWordList[wordInfo]['count'])

            if isHeader:
                dao.update('{ "word": "%s"}' % wordInfo, '{ "$set": { "postag": %s, "totalCount": %s, "headerCount": %s, "count": { "%s" : %s } } }' % (getPostagList(dbInfo["postag"], countWordList[wordInfo]["postag"]), dbInfo["totalCount"] + int(countWordList[wordInfo]['count']), dbInfo["headerCount"] + int(countWordList[wordInfo]['count']), year, dbInfo["count"][year]))
            else:
                dao.update('{ "word": "%s"}' % wordInfo, '{ "$set": { "postag": %s, "totalCount": %s, "count": { "%s" : %s } } }' % (getPostagList(dbInfo["postag"], countWordList[wordInfo]["postag"]), dbInfo["totalCount"] + int(countWordList[wordInfo]['count']), year, dbInfo["count"][year]))

        else:
            dao.insert('{"word": "%s", "postag": %s, "subject": "%s", "totalCount": %s, "headerCount": %s, "count": { "%s": %s }}' % (wordInfo, json.dumps(countWordList[wordInfo]['postag']), subject, int(countWordList[wordInfo]['count']), int(countWordList[wordInfo]['count']) if isHeader else 0, year, getCountArray(month, int(countWordList[wordInfo]['count']))))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.error("Argument error")
        logging.error("     Allowed argument :: (SERVER) (DATE) (DB_CONFIG_FILE)")
        logging.error("            DATE: yyyy-mm-dd ex> 2020-06-18")
        exit()

    sysEnv = sys.argv[1]
    date = sys.argv[2]
    dbConfigFile = sys.argv[3]

    utils = pyUtilsClass.Utils()
    pyUtilsClass.setLogging2Console()

    # config file setting
    config = utils.readJsonFile(utils.getLocalPath() + "/../config/config.json")
    NLPFileList = glob.glob(utils.getLocalPath() + "/.." + str(config["DEFAULT"]["NLPAnalysis"]["Target"]).replace("%date", date) + '/*')

    # db connection setting
    dbConfig = utils.readJsonFile(utils.getLocalPath() + "/../config/" + dbConfigFile)
    dao = setDBConnection(dbConfig[sysEnv])

    for targetFile in NLPFileList:
        jsonTarget = utils.readJsonFile(targetFile)

        contextWordCount = countWord(jsonTarget["context"])
        headlineWordCount = countWord(jsonTarget["headline"])

        crawlingDate = jsonTarget["crawlingDate"]
        subject = jsonTarget["subject"]

        countWordinDB(crawlingDate, subject, False, contextWordCount)
        countWordinDB(crawlingDate, subject, True, headlineWordCount)


    dao.setClose()











