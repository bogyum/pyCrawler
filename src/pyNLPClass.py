import logging
import nltk
from nltk.stem.wordnet import WordNetLemmatizer

class NLPAnalyzer:

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def setNLTKPath(self, path):
        nltk.data.path.append(path)

    def setLogging(self, logging):
        self.logging = logging

    def doMorphemeAnalysis(self, jsonRawData):

        for contents in jsonRawData["contents"]:
            headLine = contents["headline"]
            context = str(contents["context"]).replace("\n", ".")

            sentToken = nltk.sent_tokenize(context, "english")

            # 제목 분석
            headLineWordTokens = nltk.pos_tag(nltk.word_tokenize(headLine))

            # 본문 문장 단위 분석
            for sentence in sentToken:
                if str(sentence).find("Updated") > -1 or str(sentence).find("Reporter") > -1:
                    continue

                # tokenizing - pos tagging - lemmatizing - frequency
                logging.info("NLPAnalyzer - doMorphemeAnalysis() - sentence : %s" % sentence)

                # Tokenizing
                tokens = nltk.word_tokenize(str(sentence).lower())

                # POS Tagging
                poses = nltk.pos_tag(tokens)

                # lemmatizing
                posesList = [(p0, p1) for p0, p1 in poses if p1[:1].isalpha()]
                result = [self.lemmatizer.lemmatize(lemma[0], pos=lemma[1][:1].lower()) + '/' + lemma[1] for lemma in posesList]

                logging.info("NLPAnalyzer - doMorphemeAnalysis() - lemmatization :: %s " % result)
