#Miscellaneous tools for HunTag
def sentenceIterator(input):
    currSen = []
    for line in input:
        if line == '\n' and currSen!=[]:
            yield currSen
            currSen = []
            continue
        currSen.append(line.strip().split())
    if currSen!=[]:
        yield currSen
    return

def writeSentence(sen):
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
        self.featToNo = {}
        self.noToFeat = {}
        self.next = 1

    def getNo(self, feat):
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
