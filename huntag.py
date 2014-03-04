from collections import defaultdict
from optparse import OptionParser

from feature import Feature
from trainer import Trainer
from tagger import Tagger
from bigram import Bigram
from tools import BookKeeper, writeSentence, sentenceIterator

from os.path import isdir, join
import sys
import os


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
    for sen, _ in sentenceIterator(input):
        tags = [tok[options.tagField] for tok in sen]
        bigramModel.obsSequence(tags)
    bigramModel.count()
    bigramModel.writeToFile(options.bigramModelFile)

def main_tag(featureSet, options):
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
        writer_func = lambda s, c: writeSentence(s, comment=c)
    elif options.input_dir:
        assert isdir(options.input_dir), "--input-dir must be a directory"
        out_dir = "{}_out".format(options.input_dir)
        os.mkdir(out_dir)
        tagger_func = lambda: tagger.tag_dir(options.input_dir)
        writer_func = lambda s, c: writeSentence(
            s, out=open(join(out_dir, '{}.tagged'.format(c)), 'a'))
    else:
        tagger_func = lambda: tagger.tag_corp(sys.stdin)
        writer_func = lambda s, c: writeSentence(s, comment=c)

    for sen, other in tagger_func():
        writer_func(sen, other)

def getFeatureSet(cfgFile):
    features = {}
    optsByFeature = defaultdict(dict)
    defaultRadius = -1
    defaultCutoff = 1
    for line in open(cfgFile):
        if line == "\n" or line[0] == "#":
            continue
        feature = line.strip().split()
        if feature[0] == 'let':
            featName, key, value = feature[1:4]
            optsByFeature[featName][key] = value
            continue
        if feature[0] == "!defaultRadius":
            defaultRadius = int(feature[1])
            continue
        if feature[0] == "!defaultCutoff":
            defaultCutoff = int(feature[1])
            continue

        type, name, actionName = feature[:3]
        fields = [int(field) for field in feature[3].split(',')]
        if len(feature) > 4:
            radius = int(feature[4])
        else:
            radius = defaultRadius
        cutoff = defaultCutoff
        options = optsByFeature[name]
        feat = Feature(type, name, actionName, fields, radius, cutoff, options)
        features[name] = feat

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

    parser.add_option('-d', '--input-dir', dest='input_dir',
                      help='process all files in DIR (instead of stdin)',
                      metavar='DIR')

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
    elif task == 'train':
        featureSet = getFeatureSet(options.cfgFile)
        main_train(featureSet, options)
    elif task == 'tag':
        if options.inFeatFile:
            assert not options.input_dir, 'at most one of input-feature-file\
                    and input-dir can be specified'
            featureSet = None
        else:
            featureSet = getFeatureSet(options.cfgFile)
        main_tag(featureSet, options)
    else:
        sys.stderr.write("""invalid task: %s\nRun huntag.py --help
                            for more information\n""" % task)
    return

if __name__ == '__main__':
    main()
