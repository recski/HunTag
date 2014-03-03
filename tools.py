#Miscellaneous tools for HunTag
from collections import defaultdict
import sys
def sentenceIterator(input):
    currSen = []
    currComment = None
    while True:
        line = input.readline()
        if not line:
            break
        if line.startswith('"""'):
            assert currSen == [], 'ERROR: \
                comments are only allowed before a sentence\n'
            currComment = line.strip()
            continue
        if line == '\n' and currSen != []:
            yield currSen, currComment
            currSen = []
            currComment = None
            continue
        currSen.append(line.strip().split())
    if currSen != []:
        yield currSen, currComment
    return

def writeSentence(sen, out=sys.stdout, comment=None):
    if comment:
        out.write(comment+'\n')
    for tok in sen:
        out.write('\t'.join(tok)+'\n')
    out.write('\n')

def addTagging(sen, tags):
    taggedSen = []
    for c, tok in enumerate(sen):
        taggedSen.append(tok+[tags[c]])
    return taggedSen

def featurizeSentence(sen, features):
    sentenceFeats = [[] for _ in range(len(sen))]
    for name, feature in features.items():
        for c, feats in enumerate(feature.evalSentence(sen)):
            sentenceFeats[c] += feats
    return sentenceFeats

class BookKeeper():
    def __init__(self):
        self.featCounter = defaultdict(int)
        self.featToNo = {}
        self.noToFeat = {}
        self.next = 1

    def cutoff(self, cutoff):
        self.featCounter = dict([(feat, count)
                         for feat, count in self.featCounter.iteritems()
                         if count >= cutoff])
        keptPairs = [(feat, no) for feat, no in self.featToNo.iteritems()
                     if feat in self.featCounter]
        self.featToNo = dict(keptPairs)
        self.noToFeat = dict([(no, feat) for feat, no in keptPairs])

    def getNo(self, feat):
        self.featCounter[feat] += 1
        if not feat in self.featToNo:
            self.featToNo[feat] = self.next
            self.noToFeat[self.next] = feat
            self.next += 1
        return self.featToNo[feat]

    def saveToFile(self, fileName='featureNumbers.txt'):
        f = open(fileName, 'w')
        for feat, no in self.featToNo.iteritems():
            f.write(feat+'\t'+str(no)+'\n')
        f.close()
        return True

    def readFromFile(self, fileName='featureNumbers.txt'):
        self.featToNo = {}
        self.noToFeat = {}
        for line in file(fileName):
            l = line.strip().split()
            feat, no = l[0], int(l[1])
            self.featToNo[feat] = no
            self.noToFeat[no] = feat
            self.next = no+1
        return True
