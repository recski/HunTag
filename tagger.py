from viterbi import viterbi
from bigram import Bigram
from liblinearutil import *
from tools import *
import math
import sys

class Tagger():
    def __init__(self, featureSet, options):
        self.featureSet = featureSet
        self.params = '-b 1'
        self.lmw = options['lmw']
        modelName = options['modelName']
        sys.stderr.write('loading transition model...')
        self.transProbs = Bigram.getModelFromFile(options['bigramModelFile'])
        sys.stderr.write('done\nloading observation model...')
        self.model = load_model('{0}.model'.format(modelName))
        self.labelCounter, self.featCounter = BookKeeper(), BookKeeper()
        self.labelCounter.readFromFile('{0}.labelNumbers'.format(modelName))
        self.featCounter.readFromFile('{0}.featureNumbers'.format(modelName))
        sys.stderr.write('done\n')


    def getNumberedSenFeats(self, senFeats):
        return [ [self.featCounter.getNo(feat)
                 for feat in feats]
               for feats in senFeats]
        
    def getLogTagProbsByPos(self, senFeats):
        numberedSenFeats = self.getNumberedSenFeats(senFeats)
        contexts = [dict([(feat, 1) for feat in feats])
                           for feats in numberedSenFeats]
        dummyOutcomes = [1 for c in contexts]
        _, __, probDistsByPos = predict(dummyOutcomes, contexts,
                                        self.model, self.params)

        """
        logTagProbsByPos = [ dict([(self.featCounter.noToFeat[i+1],
                                   math.log(prob))
                                   for i, prob in enumerate(probDist)])
                                   for probDist in probDistsByPos]
        """
        
        logTagProbsByPos = []
        for probDist in probDistsByPos:
            logProbsByTag = {}
            for c, prob in enumerate(probDist):
                tag = self.labelCounter.noToFeat[c+1]
                logProbsByTag[tag] = math.log(prob)
            logTagProbsByPos.append(logProbsByTag)
        
        return logTagProbsByPos
        
    def tag(self, input):
        senCount = 0
        for sen in sentenceIterator(input):
            senCount += 1
            senFeats = featurizeSentence(sen, self.featureSet)
            logTagProbsByPos = self.getLogTagProbsByPos(senFeats)
            _, bestTagging = viterbi(self.transProbs, logTagProbsByPos,
                                     self.lmw)
            taggedSen = addTagging(sen, bestTagging)
            if senCount%1000 == 0:
                sys.stderr.write(str(senCount)+'...')
            writeSentence(taggedSen)
        sys.stderr.write(str(senCount)+'...done\n')
