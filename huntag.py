from collections import defaultdict
from optparse import OptionParser

from feature import Feature
from trainer import Trainer
from tagger import Tagger
from bigram import Bigram
from tools import BookKeeper, writeSentence, sentenceIterator

import sys


def main_train(featureSet, options, input=sys.stdin):
    optionsDict = vars(options)
    if options.usedFeats:
        optionsDict['usedFeats'] = file(options.usedFeats)
    trainer = Trainer(featureSet, optionsDict)
    if options.inFeatFile:
        trainer.getEventsFromFile(options.inFeatFile)
    else:
        trainer.getEvents(input, options.outFeatFile)
    trainer.cutoffFeats()
    trainer.train()
    trainer.save()

def main_bigramTrain(options, input):
    bigramModel = Bigram(0.000000000000001)
    for sen in sentenceIterator(input):
        tags = [tok[options.tagField] for tok in sen]
        bigramModel.obsSequence(tags)
    bigramModel.count()
    bigramModel.writeToFile(options.bigramModelFile)

def main_tag(featureSet, options, input):
    labelCounter, featCounter = BookKeeper(), BookKeeper()
    labelCounter.readFromFile('{0}.labelNumbers'.format(options.modelName))
    featCounter.readFromFile('{0}.featureNumbers'.format(options.modelName))
    optionsDict = vars(options)
    optionsDict['labelCounter'] = labelCounter
    optionsDict['featCounter'] = featCounter
    optionsDict['modelFile'] = '{0}.model'.format(options.modelName)
    tagger = Tagger(featureSet, optionsDict)
    if options.inFeatFile:
        tagger_func = lambda: tagger.tag_features(options.inFeatFile)
    else:
        tagger_func = lambda: tagger.tag_corp(input)

    for taggedSen in tagger_func():
        writeSentence(taggedSen)
        sys.stdout.flush()

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
        if len(feature)>4:
            radius = int(feature[4])
        else:
            radius = defaultRadius
        cutoff = defaultCutoff
        options = optsByFeature[name]
        feat = Feature(type,name, actionName, fields, radius, cutoff, options )
        features[name]=feat
    
    return features    

def getParser():
    parser = OptionParser()    
    parser.add_option('-c', '--config-file', dest='cfgFile',
                      help='read feature configuration from FILE',
                      metavar='FILE')

    parser.add_option('-m', '--model', dest='modelName',
                      help='name of model to be read/written',
                      metavar='NAME')

    parser.add_option('-b', '--bigram-model', dest='bigramModelFile',
                      help='name of bigram model file to be read/written',
                      metavar='FILE')                              

    parser.add_option('-l', '--language-model-weight', dest='lmw',
                      type='float', default=1,
                      help='set relative weight of the language model to L',
                      metavar='L')

    parser.add_option('-o', '--cutoff', dest='cutoff', type='int', default=1,
                      help='set global cutoff to C', metavar='C') 

    parser.add_option('-p', '--parameters', dest='trainParams',
                      help='pass PARAMS to trainer', metavar='PARAMS')

    parser.add_option('-u', '--used-feats', dest='usedFeats',
                      help='limit used features to those in FILE',
                      metavar='FILE')

    parser.add_option('-i', '--input-feature-file', dest='inFeatFile',
                      help='use training events in FILE', metavar='FILE')
     
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
        main_bigramTrain(options, sys.stdin)
    else:
        featureSet = getFeatureSet(options.cfgFile)
        if task == 'train':
            main_train(featureSet, options)
        elif task == 'tag':
            #for line in sys.stdin:
            #    foo.write(line)
            #sys.exit()
            main_tag(featureSet, options, sys.stdin)
        else:
            sys.stderr.write("""invalid task: %s\nRun huntag.py --help
                                for more information\n""" % task)
    return

if __name__=='__main__':
    main()

