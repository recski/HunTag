from tools import *
import maxent

class Trainer():
  def __init__(self, features):
    self.features = features
    self.model = maxent.MaxentModel()
    self.model.set_verbose(1)
  def addEvents(self, data):
    self.model.begin_add_event()
    for sen in sentenceIterator(data):
      for name, feature in self.features.items():
        sentenceFeats = feature.evalSentence(sen)
        for c, tok in enumerate(sen):
          context = sentenceFeats[c]
          outcome = tok[-1]
          model.add_event(context, outcome)
    
    model.end_add_event()
  
  def train(self, iter, gauss, modelFileName):
    self.model.train(iter, 'lbfgs', gauss)
    self.model.save(modelFileName)