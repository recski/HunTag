#bigram.py contains the Bigram class which implements a simple bigram model which can be built from observations of type (word1, word2). Bigram models are built and used by HunTag
import sys
import logging
import math
from collections import defaultdict

class Bigram:
    def __init__(self, smooth):
        self.reset()
        self.boundarySymbol = 'S'
        self.smooth = smooth
        self.logSmooth=math.log(self.smooth)
        self.updatewarning = 'WARNING: Probabilities have not been \
                              recalculated since last input!'
        self.tags = set()
        
    def reset(self):
        self.bigramCount=defaultdict(int)
        self.bigramLogProb={}
        self.unigramCount=defaultdict(float)
        self.unigramLogProb={}
        self.obsCount=0        
        self.updated=True        

    def obsSequence(self, sequence):
        last = self.boundarySymbol
        for tag in sequence:
            self.obs(last, tag)
            last = tag
        self.obs(last, self.boundarySymbol)
    
    def obs(self, egy, ketto):
        self.bigramCount[(egy,ketto)] += 1
        self.unigramCount[ketto] += 1
        self.obsCount+=1
        self.updated=False
  
    def count(self):
        self.tags = set()
        self.bigramLogProb = {}
        self.unigramLogProb = {}
        self.logSmooth = math.log(self.smooth)
        for pair, count in self.bigramCount.items():
            unigramCount = self.unigramCount[pair[0]]
            prob = count/unigramCount
            logProb = math.log(prob)
            #print pair, count, unigramCount, prob, logProb
            self.bigramLogProb[pair] = logProb

        for tag, count in self.unigramCount.items():
            #if tag != self.boundarySymbol:
            self.tags.add(tag)
            self.unigramLogProb[tag] = math.log(count/
                                       self.obsCount)

        self.updated=True


    def logProb(self, egy, ketto):
        if not self.updated:
            logging.warning(self.updatewarning)

        try:
            return self.bigramLogProb[(egy,ketto)]
        except KeyError:
            return self.logSmooth
  
    def prob(self, egy, ketto):
        return math.exp(self.logProb(egy,ketto)) 
  
    def writeToFile(self, fileName):
        f = open(fileName, 'w')
        f.write(str(self.smooth)+'\n')
        tagProbs = [tag+':'+str(self.unigramLogProb[tag])
                    for tag in self.tags if tag!=self.boundarySymbol]
        f.write(' '.join(tagProbs)+'\n')
        for t1 in self.tags:
            for t2 in self.tags:
                f.write('%s\t%s\t%.8f\n' % (t1, t2, self.logProb(t1,t2)))
        f.close()
  
    @staticmethod
    def getModelFromFile(fileName):
        modelFile = open(fileName)
        smooth = float(modelFile.readline())
        model = Bigram(smooth)
        tagProbs = modelFile.readline().split()
        for tagAndProb in tagProbs:
            tag, prob = tagAndProb.split(':')
            model.tags.add(tag)
            model.unigramLogProb[tag] = float(prob)
        for line in modelFile:
            l = line.split()
            t1, t2, logProb = l[0],l[1],float(l[2])
            model.bigramLogProb[(t1,t2)] = logProb
        return model
        
  
