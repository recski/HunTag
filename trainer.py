from tools import *
import maxent
maxent.set_verbose(1)

import sys

class Trainer():
  def __init__(self, features, outFeatFile=None):
    self.features = features
    self.model = maxent.MaxentModel()
    self.writeFeats = False
    if outFeatFile:
      self.writeFeats = True
      self.outFeatFile = open(outFeatFile, 'w')
  def addEvents(self, data):
    sys.stderr.write('featurizing sentences...')
    self.model.begin_add_event()
    senCount = 0
    for sen in sentenceIterator(data):
      senCount+=1
      sentenceFeats = featurizeSentence(sen, self.features)
      for c, tok in enumerate(sen):
        context = sentenceFeats[c]
        outcome = tok[-1]
        self.model.add_event(context, outcome)
        if self.writeFeats:
          self.outFeatFile.write(outcome+'\t'+' '.join(context)+'\n')
      if senCount % 1000 == 0:
        sys.stderr.write(str(senCount)+'...')
      
    self.model.end_add_event()
    sys.stderr.write(str(senCount)+'...done!\n')
    
  def train(self, iter, gauss, modelFileName):
    self.model.train(iter, 'lbfgs', gauss)
    self.model.save(modelFileName)