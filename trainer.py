#trainer.py is a module of HunTag and is used to train maxent models
from tools import *
from liblinearutil import *
import sys
from ctypes import *

class Trainer():
    def __init__(self, features, options):
        self.modelName = options['modelName']
        self.parameters = options['trainParams']
        self.cutoff = options['cutoff']
        self.features = features
        self.labels = []
        self.contexts = []
        self.labelCounter = BookKeeper()
        self.featCounter = BookKeeper()
        self.usedFeats = None
        if options['usedFeats']:
            self.usedFeats = set([line.strip()
                                  for line in options['usedFeats']])
    
    def save(self):
        sys.stderr.write('saving model...')
        save_model(self.modelName+'.model', self.model)
        sys.stderr.write('done\nsaving label and feature lists...')
        self.labelCounter.saveToFile(self.modelName+'.labelNumbers')
        self.featCounter.saveToFile(self.modelName+'.featureNumbers')
        sys.stderr.write('done\n')

    def writeFeats(self, fileName):
        featFile = open(fileName, 'w')
        for i, context in enumerate(self.contexts):
            label = self.labelCounter.noToFeat[self.labels[i]]
            feats = [self.featCounter.noToFeat[c] for c in context.keys()]
            featFile.write('{0}\t{1}\n'.format(label, ' '.join(feats)))
    
    def reduceContexts(self):
        sys.stderr.write('reducing training events...')
        self.contexts = [dict([(number, value)
                              for number, value in context.iteritems()
                              if self.featCounter.noToFeat.has_key(number)])
                         for context in self.contexts]
        sys.stderr.write('done!\n')

    def cutoffFeats(self):
        if self.cutoff<2:
            return
        sys.stderr.write('discarding features with\
        less than {0} occurences...'.format(self.cutoff))      
        self.featCounter.cutoff(self.cutoff)
        sys.stderr.write('done!\n')
        self.reduceContexts()
            
    def getEvents(self, data):
        sys.stderr.write('featurizing sentences...')
        senCount = 0
        for sen in sentenceIterator(data):
            senCount+=1
            sentenceFeats = featurizeSentence(sen, self.features)
            for c, tok in enumerate(sen):
                tokFeats = sentenceFeats[c]
                if self.usedFeats:
                    tokFeats = [feat for feat in tokFeats
                                if feat in self.usedFeats]
                featNumbers = set([self.featCounter.getNo(feat)
                               for feat in tokFeats])
                
                context = ((c_int*2)*len(featNumbers))()
                for i, no in enumerate(featNumbers):
                    context[i][1]=1
                    context[i][0]=no
                label = self.labelCounter.getNo(tok[-1])
                self.contexts.append(context)
                self.labels.append(label)
            if senCount % 1000 == 0:
                sys.stderr.write(str(senCount)+'...')
            
        sys.stderr.write(str(senCount)+'...done!\n')
        
    def train(self):
        sys.stderr.write('creating training problem...')
        prob = problem(self.labels, self.contexts)
        sys.stderr.write('done\ntraining with option(s) "'+self.parameters+'"...')
        self.model = train(prob, parameter(self.parameters))
        sys.stderr.write('done\n')
