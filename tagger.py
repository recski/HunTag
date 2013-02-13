from viterbi import viterbi
from bigram import Bigram
from liblinearutil import load_model, predict
from tools import sentenceIterator, featurizeSentence, addTagging
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
        self.labelCounter = options['labelCounter']
        self.featCounter = options['featCounter']
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
        
    
    def tag_features(self, file_name):
        sen_feats = []
        senCount = 0
        for line in file(file_name):
            if line == '\n':
                senCount+=1
                tagging = self.tag_sen_feats(sen_feats)
                yield [[tag] for tag in tagging]
                sen_feats = []
                if senCount%1000 == 0:
                    sys.stderr.write(str(senCount)+'...')
            sen_feats.append(line.strip().split())
        sys.stderr.write(str(senCount)+'...done\n')

    def tag_corp(self, input):
        senCount = 0
        for sen in sentenceIterator(input):
            senCount += 1
            senFeats = featurizeSentence(sen, self.featureSet)
            bestTagging = self.tag_sen_feats(senFeats)
            taggedSen = addTagging(sen, bestTagging)
            yield taggedSen
            if senCount%1000 == 0:
                sys.stderr.write(str(senCount)+'...')
        sys.stderr.write(str(senCount)+'...done\n')
        
    def tag_sen_feats(self, sen_feats):
        logTagProbsByPos = self.getLogTagProbsByPos(sen_feats)
        _, bestTagging = viterbi(self.transProbs, logTagProbsByPos,
                                 self.lmw)
        return bestTagging
