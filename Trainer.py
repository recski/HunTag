from tools import *
import maxent
maxent.set_verbose(1)

class Trainer():
  def __init__(self, features, outFeatFile=None):
    self.features = features
    self.model = maxent.MaxentModel()
    self.writeFeats = False
    if outFeatFile:
      self.writeFeats = True
      self.outFeatFile = open(outFeatFile, 'w')
  def addEvents(self, data):
    self.model.begin_add_event()
    for sen in sentenceIterator(data):
      sentenceFeats = [ [] for _ in range(len(sen)) ]
      for name, feature in self.features.items():
        for c, feats in enumerate(feature.evalSentence(sen)):
          sentenceFeats[c]+=feats
      
      for c, tok in enumerate(sen):
        context = sentenceFeats[c]
        outcome = tok[-1]
        self.model.add_event(context, outcome)
        if self.writeFeats:
          self.outFeatFile.write(outcome+'\t'+' '.join(context)+'\n')
    
    self.model.end_add_event()
    
  def train(self, iter, gauss, modelFileName):
    self.model.train(iter, 'lbfgs', gauss)
    self.model.save(modelFileName)