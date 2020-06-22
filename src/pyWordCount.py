# Word counting with pymongo
# -*- coding: utf8 -*-
import sys, logging, glob, json, tqdm
import pyUtilsClass, pyDAOClass

dao = pyDAOClass.DAO()

def setDBConnection(dbConfig):
    dao.setClient(dbConfig["host"], dbConfig["port"], dbConfig["id"], dbConfig["pw"])
    dao.setDB(dbConfig["database"])
    dao.setCollection(dbConfig["collections"]["wordcount"])
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

def getDailyCount(dailyCount, day, count):
    dailyCount[int(day)-1] += count
    return dailyCount

def getDailyCountInit(day, count):
    dailyCount = [0] * 31
    dailyCount[int(day) - 1] = count
    return dailyCount

def getMonthlyCount(monthlyCount, month, count):
    monthlyCount[int(month) - 1] += count
    return monthlyCount

def getMonthlyCountInit(month, count):
    monthlyCount = [0] * 12
    monthlyCount[int(month) - 1] = count
    return monthlyCount

def getSubjectCount(subjectCount, subject, count):
    subjectCount[subject] += count
    return subjectCount

def getPostagList(dbInfo, newData):
    for tag in newData:
        if not dbInfo.__contains__(tag):
            dbInfo.append(tag)
    return dbInfo

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
            "bySubject": [
                "Nat'l/Politics": xxx,
                "Sports": xxx,
            ]
        }
    }
'''
def doMakeDocument(dbInfo, wordInfo, postag, count, subject, date, isHeader, subjectJson):

    year = date.split("-")[0]
    month = date.split("-")[1]
    day = date.split("-")[2]

    # dbInfo(dictionary) 정보를 수정한 뒤에, 전체 update 로 가면 문제 없음...
    if dbInfo is None:
        dbInfo = {}

    dbInfo["word"] = wordInfo
    dbInfo["postag"] = getPostagList( (dbInfo["postag"] if 'postag' in dbInfo else []), postag)

    if "count" not in dbInfo:
        dbInfo["count"] = {}

    dbInfo["count"]["totalCount"] = count if "totalCount" not in dbInfo["count"] else dbInfo["count"]["totalCount"] + count
    dbInfo["count"]["headerCount"] = (count if "headerCount" not in dbInfo["count"] else dbInfo["count"]["headerCount"] + count) if isHeader else 0

    if "yearly" not in dbInfo["count"]:
        dbInfo["count"]["yearly"] = {}

    dbInfo["count"]["yearly"][year] = count if year not in dbInfo["count"]["yearly"] else count + dbInfo["count"]["yearly"][year]

    if "monthly" not in dbInfo["count"]:
        dbInfo["count"]["monthly"] = {}

    dbInfo["count"]["monthly"][year] = getMonthlyCountInit(month, count) if year not in dbInfo["count"]["monthly"] else getMonthlyCount(dbInfo["count"]["monthly"][year], month, count)

    if "daily" not in dbInfo["count"]:
        dbInfo["count"]["daily"] = {}

    dbInfo["count"]["daily"][year+month] = getDailyCountInit(day, count) if (year+month) not in dbInfo["count"]["daily"] else getDailyCount(dbInfo["count"]["daily"][year+month], day, count)

    if "bySubject" not in dbInfo["count"]:
        dbInfo["count"]["bySubject"] = [0] * 8

    dbInfo["count"]["bySubject"][subjectJson[subject]] += count

    return dbInfo

def countWordinDB(date, subject, isHeader, countWordList, subjectJson):

    for wordInfo in countWordList:
        dbInfo = dao.select({"word": wordInfo}, {"_id": False})

        targetData = doMakeDocument(dbInfo, wordInfo, countWordList[wordInfo]['postag'], int(countWordList[wordInfo]['count']), subject, date, isHeader, subjectJson)
        if dbInfo is None:
            #insert data
            dao.insert(targetData)
        else:
            #update data
            dao.update( {"word": wordInfo}, { '$set': targetData})

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

    for targetFile in tqdm.tqdm(NLPFileList):
        jsonTarget = utils.readJsonFile(targetFile)

        contextWordCount = countWord(jsonTarget["context"])
        headlineWordCount = countWord(jsonTarget["headline"])

        crawlingDate = jsonTarget["crawlingDate"]
        subject = jsonTarget["subject"]

        countWordinDB(crawlingDate, subject, False, contextWordCount, subjectJson)
        countWordinDB(crawlingDate, subject, True, headlineWordCount, subjectJson)


    dao.setClose()











