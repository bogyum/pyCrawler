import nltk
from nltk.stem.wordnet import WordNetLemmatizer

class NLPAnalyzer:

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def setNLTKPath(self, path):
        nltk.data.path.append(path)

    def setLogging(self, logging):
        self.logging = logging

    def getLemmatization(self, posesList):
        '''
            - 품사 리스트 확인 필요.
            - Lemmatization 이 필요한 경우의 품사 확인(필요한 어휘만 복원)
            - lemmatization 이 아닌 경우, 단어 리스트에 필요가 없는 경우 조사(리스트 제거)
                - 1. 숫자, 특수 기호
                - 2. 문자 앞/뒤에 있는 특수 기호, 혹은 숫자
        '''
        result = []
        for lemma in posesList:
            # 명사(noun), 동사(verb)
            if str(lemma[1][:1]).lower() in ['n', 'v']:
                result.append('%s/%s' % (self.lemmatizer.lemmatize(lemma[0], pos=lemma[1][:1].lower()), lemma[1]))
            # 조동사(modal), 형용사(adjective), 부사(adverb), 접속사(conjunction), 한정사(determiner), 외래어(foreign word), 의문사, 접속부사(wh-determiner,pronoun,adverb)
            elif str(lemma[1][:1]).lower() in ['m', 'j', 'r', 'c', 'f', 'w']:
                result.append('%s/%s' % (lemma[0], lemma[1]))
            '''
            # 수집 제외 단어 :: 한정사('d'eterminer), 존재어휘('e'xistential there), 전차시('p'reposition, subordinating, conjuction)
            #                순서('l'ist marker), 전치한정사, 소유격, 소유대명사('p'redeterminer, ...), 부정사('t',infinitive), 감탄사('i'nterjection)
            else:
                continue
            '''
        return result

    def doMorphemeAnalysis(self, rawText):

        sentToken = nltk.sent_tokenize(rawText, "english")

        result = []
        # 본문 문장 단위 분석
        for sentence in sentToken:
            if str(sentence).find("Updated") > -1 or str(sentence).find("Reporter") > -1:
                continue

            # tokenizing - pos tagging - lemmatizing - frequency
            # Tokenizing
            tokens = nltk.word_tokenize(str(sentence).lower())

            # POS Tagging
            poses = nltk.pos_tag(tokens)

            # lemmatizing
            posesList = [(p0, p1) for p0, p1 in poses if p1[:1].isalpha()]

            for word in self.getLemmatization(posesList):
                result.append(word)

            #result.append([word for word in self.getLemmatization(posesList)])
        return result


