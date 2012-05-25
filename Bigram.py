import sys
import logging
import math
from collections import defaultdict

class Bigram:
    def __init__(self, smooth):
        self.reset()
        self.boundarySymbol = 'S'
        self.logSmooth=math.log(smooth)
        self.updatewarning = 'WARNING: Probabilities have not been \
	                     recalculated since last input!'
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
        self.bigramLogProb={}
        self.unigramLogProb={}
	for pair, count in self.bigramCount.items():
            unigramCount = self.unigramCount[pair[0]]
            prob = count/unigramCount
            logProb = math.log(prob)
            print pair, count, unigramCount, prob, logProb
            self.bigramLogProb[pair] = logProb
	
	for tag, count in self.unigramCount.items():
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
        tags = self.unigramLogProb.keys()
        f = open(fileName, 'w')
        for t1 in tags:
            for t2 in tags:
                f.write('%s\t%s\t%.8f\n' % (t1, t2, self.logProb(t1,t2)))
        f.close()
  
    def readFromFile(self, fileName):
        if self.obsCount>0:
            logging.warning('overwriting model from file')  
        self.reset()
        for line in file(fileName):
          l = line.split()
          t1, t2, logProb = l[0],l[1],float(l[2])
          self.bigramLogProb[(t1,t2)] = logProb
       
  