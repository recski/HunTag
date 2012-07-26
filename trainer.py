#trainer.py is a module of HunTag and is used to train maxent models
from tools import *
from liblinearutil import *
import sys

class Trainer():
    def __init__(self, features, options):
        self.modelName = options.modelName        
        self.parameters = options.trainParams
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
        sys.stderr.write('saving model...')
        save_model(self.modelName+'.model', self.model)
        sys.stderr.write('done\nsaving label and feature lists...')
        self.labelCounter.saveToFile(self.modelName+'.labelNumbers')
        self.featCounter.saveToFile(self.modelName+'.featureNumbers')
        sys.stderr.write('done\n')

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
        sys.stderr.write('creating training problem...')
        prob = problem(self.labels, self.contexts)
        sys.stderr.write('done\ntraining with option(s) "'+self.parameters+'"...')
        self.model = train(prob, parameter(self.parameters))
        sys.stderr.write('done\n')
