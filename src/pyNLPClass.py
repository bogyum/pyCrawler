import nltk


class NLPAnalyzer:

    def setNLTKPath(self, path):
        self.NLTKpath = path

    def doMorphemeAnalysis(self, jsonRawData):

        return None


        '''
        sentToken = nltk.sent_tokenize(text, "english")
        for sent in sentToken:
            # 기사의 날짜와 리포터의 이름은 분석에서 제외
            if str(sent).find("Updated") > -1 or str(sent).find("Reporter") > -1:
                continue

            print("sentence :: " + sent)
            wordTokens = nltk.pos_tag(nltk.word_tokenize(sent))
            print(wordTokens)
        '''
