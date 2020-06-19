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
def countWord(wordList):
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

def getDailyCount(dailyCount, day, count):
    dailyCount[int(day)-1] += count
    return dailyCount

def getMonthlyCount(monthlyCount, month, count):
    monthlyCount[int(month) - 1] += count
    return monthlyCount

def getSubjectCount(subjectCount, subject, count):
    subjectCount[subject] += count
    return subjectCount

'''
    {
        "word": "south",
        "postag": [ "RB", "JJ", "VBP", "NN", "VB", "NNP"],
        "count": {
            "totalCount": 114,
            "headerCount": 3,
            "yearly": {
                "2020": xxxx,
            },
            "monthly": {
                "2020": [0,0,0,0,114,0,0,0,0,0]
            },
            "daily": {
                "202005": [0,0,0,0,0,0,0,0,0, ..... ],
                "202006": [0,0,0,0,0,0,0,0,0, ..... ]
            },
            "bySubject": {
                "Nat'l/Politics": xxx,
                "Sports": xxx,
            }
        }
    }
    '''
# word, postag, count, subject, date,isHeader
def getInsertData(word, postag, count, subject, date, isHeader, subjectJson):
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]

    monthlyCount = [0] * 12
    dailyCount = [0] * 31
    subjectCount = [0] * 8
    result = '{"word": "%s", "postag": %s, "count": { "totalCount": %s, "headerCount": %s, "yearly": { "%s": %s }, "monthly": { "%s": %s }, "daily": { "%s": %s }, "bySubject": %s }}' \
             % (word, json.dumps(postag), count, count if isHeader else 0, year, count, year, getMonthlyCount(monthlyCount, month, count), year+month, getDailyCount(dailyCount, day, count), getSubjectCount(subjectCount, subjectJson[subject], count))

    return result

def getUpdateData(dbInfo, postag, count, subject, date, isHeader, subjectJson):
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]

    result = ('{"$set": {"postag": %s, "count": {"totalCount": %s, "headerCount": %s, "yearly": {"%s": %s}, "monthly": {"%s": %s}, "daily": {"%s": %s}, "bySubject": %s }}}' % \
              (getPostagList(dbInfo["postag"], postag), dbInfo["count"]["totalCount"] + count, dbInfo["count"]["headerCount"] + count if isHeader else dbInfo["count"]["headerCount"], \
               year, dbInfo["count"]["yearly"][year] + count, \
               year, getMonthlyCount(dbInfo["count"]["monthly"][year], month, count), \
               year+month, getDailyCount(dbInfo["count"]["daily"][year+month], day, count), \
               getSubjectCount(dbInfo["count"]["bySubject"], subjectJson[subject], count)))

    return result

def countWordinDB(date, subject, isHeader, countWordList, subjectJson):

    for wordInfo in countWordList:
        dbInfo = dao.select('{"word": "%s"}' % wordInfo)

        if dbInfo is None:
            #insert data
            # word, postag, count, subject, date,isHeader
            dao.insert(getInsertData(wordInfo, countWordList[wordInfo]['postag'], int(countWordList[wordInfo]['count']), subject, date, isHeader, subjectJson))
        else:
            #update data
            dao.update('{"word": "%s"}' % wordInfo, getUpdateData(dbInfo, countWordList[wordInfo]['postag'], int(countWordList[wordInfo]['count']), subject, date, isHeader, subjectJson))

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

    # subject json
    subjectJson = utils.readJsonFile(utils.getLocalPath() + "/../config/subject.json")

    for targetFile in NLPFileList:
        jsonTarget = utils.readJsonFile(targetFile)

        contextWordCount = countWord(jsonTarget["context"])
        headlineWordCount = countWord(jsonTarget["headline"])

        crawlingDate = jsonTarget["crawlingDate"]
        subject = jsonTarget["subject"]

        countWordinDB(crawlingDate, subject, False, contextWordCount, subjectJson)
        countWordinDB(crawlingDate, subject, True, headlineWordCount, subjectJson)


    dao.setClose()











