import nltk, logging

class NLPAnalyzer:

    def setNLTKPath(self, path):
        nltk.data.path.append(path)

    def setLogging(self, logging):
        self.logging = logging

    def doMorphemeAnalysis(self, jsonRawData):

        for contents in jsonRawData["contents"]:
            headLine = contents["headline"]
            context = str(contents["context"]).replace("\n", ".")

            sentToken = nltk.sent_tokenize(context, "english")

            # Need to add progress bar
            for sentence in sentToken:
                if str(sentence).find("Updated") > -1 or str(sentence).find("Reporter") > -1:
                    continue

                logging.info("      NLPAnalyzer Class() - sentence :: %s" % sentence)
                wordTokens = nltk.pos_tag(nltk.word_tokenize(sentence))
