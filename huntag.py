from collections import defaultdict
from optparse import OptionParser

import maxent
maxent.set_verbose(1)

from viterbi import viterbi

from feature import Feature
from trainer import Trainer
from bigram import Bigram
from tools import *

import math
import sys

def main_maxentTrain(modelFile, featureSet, options, input=sys.stdin):
    trainer = Trainer(featureSet, options.outFeatFile)
    trainer.addEvents(input)
    trainer.train(options.iter, options.gauss, modelFile)

def main_bigramTrain(modelFile, tagField, input=sys.stdin):
    bigramModel = Bigram(0.00000001)
    for sen in sentenceIterator(input):
        tags = [tok[tagField] for tok in sen]
        bigramModel.obsSequence(tags)
    bigramModel.count()
    bigramModel.writeToFile(modelFile)
        
def main_tag(maxentModelFile, bigramModelFile, featureSet, options, input=sys.stdin):
    sys.stderr.write('loading transition model...')
    transProbs = Bigram.getModelFromFile(bigramModelFile)
    sys.stderr.write('done\nloading maxent model...')
    maxentModel = maxent.MaxentModel()
    maxentModel.load(maxentModelFile)
    senCount = 0
    sys.stderr.write('done\ntagging...')
    for sen in sentenceIterator(input):
        senCount += 1
        senFeats = featurizeSentence(sen, featureSet)
        tagProbsByPos = [dict(maxentModel.eval_all(feats)) for feats in senFeats]
        logTagProbsByPos = [dict([(tag, math.log(prob)) for tag, prob in d.items()]) for d in tagProbsByPos]
        _, bestTagging = viterbi(transProbs, logTagProbsByPos, options.lmw)
        taggedSen = addTagging(sen, bestTagging)
        if senCount%1000 == 0:
            sys.stderr.write(str(senCount)+'...')
        writeSentence(taggedSen)
    sys.stderr.write(str(senCount)+'...done\n')

def getFeatureSet(cfgFile):
    features = {}
    optsByFeature = defaultdict(dict)
    defaultRadius = -1
    defaultCutoff = 1
    for line in open(cfgFile):
        if line=="\n" or line[0]=="#":
            continue
        feature=line.strip().split()
        if feature[0]=='let':
            featName, key, value = feature[1:4]
            optsByFeature[featName][key] = value
            continue
        if feature[0]=="!defaultRadius":
            defaultRadius = int(feature[1])
            continue
        if feature[0]=="!defaultCutoff":
            defaultCutoff = int(feature[1])
            continue
        
        type, name, actionName = feature[:3]
        fields = [ int(field) for field in feature[3].split(',') ]
        radius = defaultRadius
        cutoff = defaultCutoff
        options = optsByFeature[name]
        feat = Feature( type, name, actionName, fields, radius, cutoff, options )
        features[name]=feat
    
    return features    

def getParser():
    parser = OptionParser()    
    parser.add_option('-c', '--config-file', dest='cfgFile',
                      help='read feature configuration from FILE',
                      metavar='FILE')
    parser.add_option('-m', '--maxent-model', dest='maxentModelFile',
                      help='name of maxent model file to be read/written',
                      metavar='FILE')
    parser.add_option('-b', '--bigram-model', dest='bigramModelFile',
                      help='name of bigram model file to be read/written',
                      metavar='FILE')
    parser.add_option('-i', '--iterations', dest='iter', type='int',
                      help='train with a maximum of N iterations', metavar='N')
                                       
    parser.add_option('-g', '--gauss', dest='gauss', type='int', default=0,
                      help='train using a Gaussian penalty of N', metavar='N')
                                       
    parser.add_option('-l', '--language-model-weight', dest='lmw',
		              type='float', default=0.5,
		              help='set relative weight of the language model to L',
                      metavar='L')
                                        
    parser.add_option('-f', '--feature-file', dest='outFeatFile',
                      help='write training events to FILE', metavar='FILE')
                                        
    parser.add_option('-t', '--tag-field', dest='tagField', type='int',
                      help="""specify FIELD containing the tags to build bigram
		              model from""", metavar='FIELD')
    return parser
    
def main():
    parser = getParser()
    options, args = parser.parse_args()
    task = args[0]
    if task == 'bigram-train':
        main_bigramTrain(options.bigramModelFile, options.tagField)
    else:
        featureSet = getFeatureSet(options.cfgFile)
        if task == 'maxent-train':
            main_maxentTrain(options.maxentModelFile, featureSet, options)
        elif task == 'tag':
            main_tag(options.maxentModelFile, options.bigramModelFile,
                             featureSet, options)
        else:
            sys.stderr.write("""invalid task: %s\nRun huntag.py --help
			                    for more information\n""" % task)
    return

if __name__=='__main__':
    main()

