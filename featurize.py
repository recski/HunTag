#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#import inverz

from Feature import Feature
import Lexicon

try :
  import psyco
  psyco.full()
except :
  sys.stderr.write("Module psyco is not installed. Please note that this may mean a ~100% speed penalty.\n\n")


def process(adat):
  """korpuszbol (soronkent 1 token, mondatonkent ures sor) csinal corp nevu listat, melynek elemei mondatok, melynek elemei szavak, melynek elemei mezok"""
  corp=[[]] #mondatok listaja
  recLengths = set()
  dc = 0
  for line in adat:
    dc += 1
    if line == '\n':
      corp.append([])
    else:
      v = line.strip("\n").split()
      corp[-1].append(v)
      recLengths.add(len(v))
      if len(v)==1: sys.stderr.write(str(v))
  if len(recLengths)!=1 :
    sys.stderr.write( "Inconsistent record lengths in corpus.\n" )
    #sys.stderr.write(str(len(v)))
    #sys.stderr.write(str(v))
    
    sys.exit(-1)
  return (corp,recLengths.pop())
			      

def getSentenceFeatures(sen, feats, keepZero):

  sentenceFeatures=[]
  
  valuesByFeature=[feats[feature].evalSentence(sen, keepZero) for feature in feats]
  
  for pos,word in enumerate(sen):
    wordFeatures=[]
    
    for featCount,feat in enumerate(feats):    
      wordFeatures+=valuesByFeature[featCount][pos]
      
    #if pos<5:
    #  wordFeatures.append(str(-pos-1)+'_B')
    #if pos>len(sen)-6:
    #  wordFeatures.append(str(len(sen)-pos)+'_B')
    
    
    #sys.stderr.write(str(wordFeatures))
    
    tag = word[-1]
    sentenceFeatures.append( ( wordFeatures, tag ) )
    
    
    
  #sys.stderr.write(str(sentenceFeatures))
  #sys.exit(-1)
  
  return sentenceFeatures


def featurizeSentenceWithTags(sen, feats):

  sentenceFeatures=getSentenceFeatures(sen, feats, keepZero)

  for i in range (len(sen)):
    sentenceFeatures[i].append('prevtag='+sen[i-1][-1])    
  
  return sentenceFeatures



def featurizeSentence(sen, feats, includeTag, keepZero):
  if includeTag:
    features = featurizeSentenceWithTags(sen, feats, keepZero)
  else:
    features = getSentenceFeatures(sen, feats, keepZero)
  
  return features
  
    
def featurizeCorpus(corp, options, includeTag):
  sys.stderr.write('featurizing... ')
  features=[]
  for c,sen in enumerate(corp):
     if 100*c/len(corp)>100*(c-1)/len(corp):
       sys.stderr.write(str((100*c)/len(corp))+'% ')
     features += featurizeSentence(sen,options, includeTag)
     features.append(None)
  sys.stderr.write("\n")
  return features


def dumpFeatures(features):
  #sys.stderr.write(str(features))
  for event in features :
    if event :
      #sys.stderr.write(str(event[1]))
      #print event[1] + "\t" + " ".join([e for e in event[0] if e[-1]!=0])
      print event[1] + "\t" + " ".join(sorted(event[0]))
    else :
      print ""

def featurizeCorpusToStdout(corp,feats, includeTag, emptyLines, keepZero):
  sys.stderr.write('featurizing... ')
  recLength = None
  currSen = []
  for line in sys.stdin:
    if line == '\n':
      if recLength == None: continue
      dumpFeatures( featurizeSentence(currSen, feats, includeTag, keepZero) )
      if emptyLines:
        print
      currSen = []
      continue
    l = line.split()
    if recLength == None:
      recLength = len(l)
    elif len(l)!=recLength:
      sys.stderr.write( "Inconsistent record lengths in corpus.\n" )
      sys.stderr.write( "Offending line:\n"+line+'Assumed record length:\n'+str(recLength))
      sys.exit(-1)
    
    currSen.append(l)
  sys.stderr.write("done!\n")  
  
  """  
  for c,sen in enumerate(corp):
     if 100*c/len(corp)>100*(c-1)/len(corp):
       sys.stderr.write(str((100*c)/len(corp))+'% ')
     dumpFeatures( featurizeSentence(sen,feats, includeTag) )
     if emptyLines:
       print
  sys.stderr.write("\n")
  """


def getOptions(file):
  features = {}
  f=open(file)
  
  optsByFeature = {}
  
  defaultRadius = -1
  for line in f.readlines():
    if line=="\n" or line[0]=="#" :
      continue
    feature=line.strip().split()

    if feature[0]=='let':
      assert len(feature)==4
      featName, key, value = feature[1:4]
      try:
        value = int(value)
      except:
        try:
          value = float(value)
        except:
          pass
      
      if optsByFeature.has_key(featName):
        if optsByFeature[featName].has_key(key):
          sys.stderr.write('option "'+key+'" of feature "'+featName+' defined more than once!')
          sys.exit(-1)
          
        optsByFeature[featName][key] = value
      else:
        optsByFeature[featName] = {key:value}
      
      continue
    
    if feature[0][0]=="!" :
	# command
	assert feature[0]=="!defaultRadius"
	defaultRadius = int(feature[1])
	continue

    if len(feature) not in (4,5) :
	sys.stderr.write( "Incorrect number of fields: "+line )
	sys.exit(-1)

    kind, name, actionName = feature[0:3]
    fields = [ int(field) for field in feature[3].split(',') ]
    
    assert kind in ("token","lex","sentence")

    if len(feature)!=4 :
      assert len(feature)==5
      radius = int(feature[4])
    else :
      if defaultRadius==-1 :
        sys.stderr.write("If no !defaultRadius is specified then you must set each radius in the 5th fields of features.\n" ) 
	sys.exit(-1)
      radius = defaultRadius
      
    options = optsByFeature.get(name, {})
    
    feat = Feature( kind, name, actionName, fields, radius, options )
    features[name]=feat
  
  return features




def main(featuresFile=None, emptyLines=False, withTags=False, z_keepZero=False):
  options=getOptions(featuresFile)
  featurizeCorpusToStdout(sys.stdin, options, withTags, emptyLines, z_keepZero)

import optfunc
if __name__ == '__main__' :
  optfunc.run(main)