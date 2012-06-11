
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
