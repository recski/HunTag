#Miscellaneous tools for HunTag
# vim: set expandtab: 
from collections import defaultdict
def sentenceIterator(input):
    currSen = []
    currComment = None
    while True:
        line = input.readline()
        if not line:
            break
        if line.startswith('"""'):
            if currSen:
                sys.stderr.write('ERROR: comments are only allowed before a sentence\n')
                sys.exit(-1)
            else:
                curComment = line.strip()
                continue
        if line == '\n' and currSen!=[]:
            yield currSen, curComment
            currSen = []
            currComment = None
            continue
        currSen.append(line.strip().split())
    if currSen!=[]:
        yield currSen, curComment
    return

def writeSentence(sen, comment):
    print comment
    for tok in sen:
        print '\t'.join(tok)
    print

def addTagging(sen, tags):
    taggedSen = []
    for c, tok in enumerate(sen):
        taggedSen.append(tok+[tags[c]])
    return taggedSen

def featurizeSentence(sen, features):      
    sentenceFeats = [ [] for _ in range(len(sen)) ]
    for name, feature in features.items():
        for c, feats in enumerate(feature.evalSentence(sen)):
            sentenceFeats[c]+=feats
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
                         if count>=cutoff])
        keptPairs = [(feat, no) for feat, no in self.featToNo.iteritems()
                     if self.featCounter.has_key(feat)]
        self.featToNo = dict(keptPairs)
        self.noToFeat = dict([(no, feat) for feat, no in keptPairs])        

    def getNo(self, feat):
        self.featCounter[feat]+=1
        if not self.featToNo.has_key(feat):
            self.featToNo[feat] = self.next
            self.noToFeat[self.next] = feat
            self.next+=1
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
