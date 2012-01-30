import sys

from collections import defaultdict
from optparse import OptionParser

from Feature import Feature
from Trainer import Trainer
from tools import *

def main_maxentTrain(modelFile, featureSet, options):
  trainer = Trainer(featureSet, options.outFeatFile)
  trainer.addEvents(sys.stdin)
  trainer.train(options.iter, options.gauss, modelFile)

def main_bigramTrain(modelFile):
  pass
  
def main_tag(modelFile, featureSet):
  pass


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
  parser.add_option('-i', '--iterations', dest='iter', type='int',
                    help='train with a maximum of N iterations', metavar='N')
  parser.add_option('-g', '--gauss', dest='gauss', type='int', default=0,
                    help='train using a Gaussian penalty of N', metavar='N')
  parser.add_option('-l', '--language-model-weight', dest='lmw', type='float',
                    default=0.5,
                    help='set relative weight of the language model to L',
                    metavar='L')
  parser.add_option('-f', '--feature-file', dest='outFeatFile',
                    help='write training events to FILE', metavar='FILE')
  return parser
  
def main():
  parser = getParser()
  options, args = parser.parse_args()
  task, modelFile = args[:2]
  if task == 'bigram-train':
    main_bigramTrain(modelFile)
  else:
    cfgFile = args[2]
    featureSet = getFeatureSet(cfgFile)
    if task == 'maxent-train':
      main_maxentTrain(modelFile, featureSet, options)
    elif task == 'tag':
      main_tag(modelFile, featureSet)
    else:
      sys.stderr.write('invalid task: %s\n'+
                       'Run huntag.py --help for more information\n' % task)
  return

if __name__=='__main__':
  main()

