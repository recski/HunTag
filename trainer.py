#trainer.py is a module of HunTag and is used to train maxent models
from tools import *
from liblinear.python.liblinearutil import *
import sys

class Trainer():
    def __init__(self, features, options):
        self.modelName = options.modelName        
        self.parameters = parameter(options.trainParams)
        self.features = features
        self.labels = []
        self.contexts = []
        self.labelCounter = BookKeeper()
        self.featCounter = BookKeeper()
        self.writeFeats = False
        if options.outFeatFile:
            self.writeFeats = True
            self.outFeatFile = open(outFeatFile, 'w')
    
    def save(self):
        save_model(self.modelName+'.model', self.model)
        self.labelCounter.saveToFile(self.modelName+'.labelNumbers')
        self.featCounter.saveToFile(self.modelName+'.featureNumbers')

    def getEvents(self, data):
        sys.stderr.write('featurizing sentences...')
        senCount = 0
        for sen in sentenceIterator(data):
            senCount+=1
            sentenceFeats = featurizeSentence(sen, self.features)
            for c, tok in enumerate(sen):
                tokFeats = sentenceFeats[c]
                featNumbers = [self.featCounter.getNo(feat) for feat in tokFeats]
                context = dict([(featNo, 1) for featNo in featNumbers])
                label = self.labelCounter.getNo(tok[-1])
                self.contexts.append(context)
                self.labels.append(label)
                if self.writeFeats:
                    self.outFeatFile.write(tok[-1]+'\t'+' '.join(tokFeats)+'\n')
            if senCount % 1000 == 0:
                sys.stderr.write(str(senCount)+'...')
            
        sys.stderr.write(str(senCount)+'...done!\n')
        
    def train(self):
        prob = problem(self.labels, self.contexts)
        self.model = train(prob, self.parameters)
