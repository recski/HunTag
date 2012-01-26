
import math
import Bigram

def getType(tag) :
  legalParts = ('B', 'I', 'E', '1')
  if tag == 'O':
    return tag
  else:
    assert tag[1]=='-' and tag[0] in legalParts
    return tag[2:]

def segmentCounts(corp, tags) :
  #(currSeg, prevSeg --> length)
  freqMap = {}
  bgFreqMap = {}
  segFreqs = {}
  fTags = tags.copy()
  fTags.add('S')
  for tag1 in fTags :
    segFreqs[tag1] = 0
    for tag2 in fTags :
      freqMap[(tag1,tag2)] = {}
      bgFreqMap[(tag1, tag2)] = 0
  
  for sen in corp :
    prevSeg = 'S'
    currSeg = 'S'
    currSegLength = None
    for tok in sen :
      type = getType(tok[-1])
      part = tok[-1][0]
      if type!=currSeg or part in ('B', '1') :
        segFreqs[type] += 1
        #print currSeq, prevSeq, bgFreqMap
        bgFreqMap[(currSeg, prevSeg)] += 1
        
        try :
          freqMap[(currSeg, prevSeg)][currSegLength] += 1
        except KeyError :
          freqMap[(currSeg, prevSeg)][currSegLength] = 1
        
        prevSeg = currSeg
        currSeg = type
        currSegLength = 1
      
      else:
        currSegLength += 1

  return freqMap, bgFreqMap, segFreqs
  
def printStats(freqMap, bgFreqMap):
  for pair, bgFreq in bgFreqMap.iteritems() :
    if freqMap[pair].keys()==[] or pair==('S', 'S') :
      continue
    print ' '.join(pair)
    lengths = range(max(freqMap[pair].keys())+1)
    for l in lengths :
      print '\t'.join([str(l), str(freqMap[pair].get(l, 0))])  
    print


class SegmentModel :
  
  def __init__(self, corp, typeSet, smooth):
    
    self.segmentTransitionModel = buildSegmentTransitionModel(corp, typeSet, smooth)
    self.segmentLengthModel = buildSegmentLengthModel(corp, typeSet)
    
    #self.segmentTransitionModel = segmentTransitionModel
    #self.segmentLengthModel = segmentLengthModel
    self.smooth=smooth
        
    self.bgModel = Bigram.transprobs(corp, -1)
    
  
  
  def segmentLogProb(self,prevTag,tag,length):
    transitionLogProb = self.segmentTransitionModel[prevTag].get(tag, self.smooth)
    lengthLogProb = self.segmentLengthModel[tag].get(length, self.smooth)
    
    #return transitionLogProb+lengthLogProb
    
    return self.segmentTransition(prevTag, tag, length)
  
  def segmentTransition(self, prevTag, tag, length):
    if prevTag != 'O':
      biePrevTag='E-'+prevTag
    else:
      biePrevTag=prevTag
    if tag != 'O':
      if length==1 :
        bieTag = '1-'+tag
      else :
        bieTag = 'B-'+tag
    else:
      bieTag = tag
      
    transition = self.bgModel.logProb(biePrevTag, bieTag)
    if tag=="O" :
      transition += self.bgModel.logProb('O','O') * (length-1)
    else :
      if length>1 :
        if length>2 :
          transition += self.bgModel.logProb('B-'+tag, 'I-'+tag)
          transition += self.bgModel.logProb('I-'+tag, 'I-'+tag) * (length-3)
          transition += self.bgModel.logProb('I-'+tag, 'E-'+tag)
        else :
          transition += self.bgModel.logProb(bieTag, 'E-'+tag)
    transProb = transition
    
    return transProb


def buildSegmentLengthModel(corp, tags):
  segCount={}
  segLengths={}
  for tag in tags:
    segCount[tag]=0
    segLengths[tag]={}
  for sen in corp:
    currSeg=None
    currSegLength=None
    for tok in sen:
      type=getType(tok[-1])
      assert type!=None
      if type == currSeg:
        currSegLength +=1
        continue
      
      if currSeg == None:
        segCount[type]+=1
        currSeg = type
        currSegLength = 1
        continue

      try:
        segLengths[currSeg][currSegLength]+=1
      except KeyError:
        segLengths[currSeg][currSegLength]=1

      segCount[type]+=1  
      currSeg = type
      currSegLength = 1
    
    if currSeg == None:
      continue
      
    try:
        segLengths[currSeg][currSegLength]+=1
    except KeyError:
        segLengths[currSeg][currSegLength]=1    

  segmentLengthModel={}
  for tag in tags:
    segmentLengthModel[tag]={}
    tagFreq=float(segCount[tag])
    for length, freq in segLengths[tag].iteritems():
      segmentLengthModel[tag][length]=math.log(freq/tagFreq)

  return segmentLengthModel

def buildSegmentTransitionModel(corp, typeSet, smooth):
  fTypeSet=typeSet.copy()
  fTypeSet.add('S')
  dummy, bgFreq, segFreq = segmentCounts(corp, fTypeSet)
  segmentTransitionModel = {}
  for prevTag in fTypeSet:
    segmentTransitionModel[prevTag] = {}
    for tag in fTypeSet:
      pairFreq = float(bgFreq[(tag, prevTag)])
      prevFreq = segFreq[prevTag]
      if pairFreq and prevFreq:
        segmentTransitionModel[prevTag][tag] = math.log(pairFreq/prevFreq)
      else:
        segmentTransitionModel[prevTag][tag] = smooth
  return segmentTransitionModel


if __name__=='__main__':
  import sys
  import featurize
  input = sys.stdin.readlines()
  corp,lR = featurize.process(input)
  #tags=('NP', 'O', 'S')
  tags = [getType(line.strip('\n').split()[-1]) for line in input if line != '\n']
  tagSet = set(tags)
  tagSet.add('S')
  sys.stderr.write(str(tagSet))
  freqMap, bgFreqMap, segFreqs = segmentCounts(corp, tagSet)
  printStats(freqMap, bgFreqMap)
