#lexicon.py is a module of HunTag and is called by the module feature.py
#the Lexicon class generates so-called lexicon features
#an instance of Lexicon() should be initialized for each lexicon file
import sys

class Lexicon():
    def __init__(self, file):
        sys.stderr.write('opening '+file+'\n')
        self.list = set()
        self.endParts = set()
        self.midParts = set()
        self.startParts = set()
        for line in open(file):
            phrase = line.strip()
            self.list.add(phrase)
            words = line.split()
            if len(words)>1:
                self.endParts.add(words[-1])
                self.startParts.add(words[0])
                if len(words)>2:
                    for w in words[1:-1]:
                        self.midParts.add(w)
        
    def getWordFeats(self, word):
        wordFeats = []
        if word in self.list:
            wordFeats.append('lone')
        if word in self.endParts:
            wordFeats.append('end')
        if word in self.startParts:
            wordFeats.append('start')
        if word in self.midParts:
            wordFeats.append('mid')
        
        return wordFeats
        
    def lexEvalSentence(self, sentence):
        featVec=[]
        for word in sentence:
            featVec.append(self.getWordFeats(word))
        return featVec
    
