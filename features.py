#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys

nonalf=re.compile(r'\W+')
casCode=re.compile(r'CAS<...>')


def stupidStem(form) :
    r = form.rfind("-")
    if r==-1 :
        return form
    else :
        return form[:r]

#az eredeti isCapitalizedOperator, de ez csak azt nezi, hogy van-e benne nagybetu BARHOL
def isCapitalizedOperator(form) :
    return [int( form.lower() != form )]

#uj nevet adtam neki
def hasCapOperator(form) :
    return [int( form.lower() != form )]

#uj: csupa kisbetu
def lowerCaseOperator(form):
    return [int(form.lower() == form)]   

#ez az uj isCapitalized: nagybetuvel kezdodik
def isCapOperator(form) :    
    return [int( form[0] != form[0].lower())]

#ez is uj: kisbetuvel kezdodik
def notCapitalizedOperator(form):
    return [int(form[0] == form[0].lower())]

def isAllcapsOperator(form) :
    return [int( stupidStem(form).isupper() )]

# Az elso betut levagjuk. A tobbi kozott van-e nagy? De ne legyen mind az.
def isCamelOperator(form) :
    if isAllcapsOperator(form) :
        return [int(False)]
    else :
        return [int( form[1:].lower() != form[1:] )]

def threeCaps(form):
  if len(form)==3 and isAllcapsOperator(form)==[1]:
    return [1]
  else:
    return [0]


def startsWithNumberOperator(form) :
    return [int( form[0].isdigit() )]

def isNumberOperator(form) :   
    for c in stupidStem(form) :
        if not ( c in ['0','1','2','3','4','5','6','7','8','9'] or c in [ ',','.','-','%' ] ) :
            return [int(False)]
    return [int(True)]

def hasNumberOperator(form) :
    for c in form :
        if c in ['0','1','2','3','4','5','6','7','8','9'] :
            return [int(True)]
    return [int(False)]


def hasDashOperator(form):
    hasDash = False
    for c in form:  
        if c is '-':
            return [int(True)]
    return [int(False)]

def hasPeriodOperator(form):
    hasPeriod = False
    for c in form:  
        if c is '.':
            return [int(True)]
    return [int(False)]

def sentenceStart( surfaceformVector ) :
    featureVector = []
    for formIndex,form in enumerate(surfaceformVector) :
        if form=="" :
            featureVector.append("")
        else :
            val = 0
            if formIndex>0 :
                val = ( surfaceformVector[formIndex-1]=="" and 1 or 0 )
            else :
                val = 1
            featureVector.append( val )
    return featureVector

def sentenceEnd( surfaceformVector ) :
    featureVector = []
    for formIndex,form in enumerate(surfaceformVector) :
        if form=="" :
            featureVector.append("")
        else :
            val = 0
            if formIndex+1<len(surfaceformVector) :
                val = ( surfaceformVector[formIndex+1]=="" and 1 or 0 )
            else :
                val = 1
            featureVector.append( val )
    return featureVector

smallcase='aábcdeéfghiíjklmnoóöõpqrstuúüûvwxyz'
bigcase='AÁBCDEÉFGHIÍJKLMNOÓÖÕPQRSTUÚÜÛVWXYZ'

big2small={}
for i in range (len(bigcase)):
  big2small[bigcase[i]]=smallcase[i]
  


def longPattern(form):
  pattern=''
  for char in form:
    if char in smallcase:
      pattern+='a'
    elif char in bigcase:
      pattern+='A'
    else:
      pattern+='_'
  
  return [ pattern ]

def shortPattern(form):
  pattern=''
  prev=''
  for char in form:
    if char in smallcase:
      if prev=='a':
        pass
      else:
        pattern+='a'
        prev='a'
    elif char in bigcase:
      if prev=='A':
        pass
      else:
        pattern+='A'
        prev='A'
    else:
      if prev=='_':
        pass
      else:
        pattern+='_'
        prev='_'
        
  return [ pattern ]

def scase(word):
  """kisbetus verziot ad vissza"""
  for i in range(35):	
    if word[0]==bigcase[i]:
      return smallcase[i]+word[1:]
  
  return [ word ]


def isInRangeWithSmallCase(word):
  #sys.stderr.write(word+'\n')
  range=30
  if word[0] in smallcase:
    return 'n/a'
  else:
    a=int(db.isInRange(scase(word), range, wordcount))
    return [ a ]

def chunkTag(chunktag):
  return [ chunktag ]

def chunkType(chunktag):
  return [ chunktag[2:] ]

def chunkPart(chunktag):
  return [ chunktag[0] ]

def getForm(word):
  if '_' not in word:
    return [word]
  else:
    return ['MERGED']
    
#def ngrams(word, n=3) :
#  f=[]
#  for c in range(max(0, len(word)-n+1)):
#    if c==0:
#      f.append('@'+str(word[c:c+n]))
#    elif c+n == len(word):
#      f.append(str(word[c:c+n])+'@')
#    else:
#      f.append(str(word[c:c+n]))
#  return f

def ngrams(word, options) :
  n = options['n']
  f=[]
  for c in range(max(0, len(word)-n+1)):
    if c==0:
      f.append('@'+str(word[c:c+n]))
    elif c+n == len(word):
      f.append(str(word[c:c+n])+'@')
    else:
      f.append(str(word[c:c+n]))
  return f


def msdPos(msd):
  return msd[1]

def msdPosAndChar(msd):
  pos = msd[1]
  f=[]
  for c,ch in enumerate(msd[2:-1]):
    if ch == '-':
      pass
    else:
      f.append (pos+str(c)+ch)
  return f

def prefix(word, options):
  n = options['n']
  return  [ word[0:n] ] 

def suffix(word, options):
  n = options['n']
  return  [ word[-n:] ]


def lemmaLowered(word, lemma):
  
  if word[0] not in bigcase: 
    if lemma[0] in bigcase:
      if big2small[lemma[0]]==word[0]: return ['raised']
    
    return ['N/A']
  
  if word[0] == lemma[0]: return [0]
  
  if big2small[word[0]]==lemma[0]: return [1]
  
  return ['N/A']

def krPieces(kr) :
  pieces=nonalf.split(kr)
  pos=pieces[0]
  feats=[]
  last = ""
  for koddarab in pieces:
    if koddarab=='PLUR':
      processed = pos+"_PLUR"
    else:
      if koddarab in ('1','2') :
        processed = last+"_"+koddarab
      else :
        processed = koddarab
    
    feats.append(processed)
    last = koddarab
  
  return [ feat for feat in feats if feat ]
  

def fullKrPieces(kr):
  return krPieces('/'.join(kr.split('/')[1:]))

def krFeats(kr) :
  pieces=nonalf.split(kr)[1:]
  feats=[]
  last = ""
  for koddarab in pieces:
    if koddarab in ('1','2') :
      processed = last+"_"+koddarab
    else :
      processed = koddarab
    
    feats.append(processed)
    last = koddarab
  
  return [ feat for feat in feats if feat ]  
  
def krConjs(kr) :
  pieces=nonalf.split(kr)
  feats=[]
  conjs=[]
  
  for ind,e1 in enumerate(pieces):
    for e2 in pieces[ind+1:]:
      if e2 == '': continue
      conjs.append(e1+'+'+e2)
  
  return [ feat for feat in conjs if feat ]




def capsPattern( sentence, fields ) :
  featVec = [ [] for word in sentence ]

  assert len(fields)==1
  tokens = [ word[fields[0]] for word in sentence ]
  upperFlags = [ isCapitalizedOperator(token)[0] for token in tokens ]
  start = -1
  mapStartToSize = {}
  for pos,flag in enumerate( upperFlags+[0] ) :
    if flag==0 :
      if start!=-1 :
        mapStartToSize[start] = pos-start
      start = -1
      continue
    else :
      if start==-1 :
        start = pos
  if start!=-1 :
    mapStartToSize[start] = len(upperFlags)-start

  for pos,flag in enumerate(upperFlags) :
    if flag==0 :
      start = -1
      continue
    if start==-1 :
      start = pos
    positionInsideCapSeq = pos-start
    lengthOfCapSeq = mapStartToSize[start]
    p = str(positionInsideCapSeq)
    l = str(lengthOfCapSeq)
    featVec[pos] += [ "p"+p, "l"+l, "p"+p+"l"+l ]

  return featVec

def capsPattern_test() :
  tokens = [ "A", "certain", "Ratio", "Of", "GDP", "is", "Gone", "Forever" ]
  sentence = [ [token] for token in tokens ]
  fields = [0]
  print capsPattern( sentence,fields )

def isBetweenSameCases(sentence, fields, maxDist=6):
  featVec = [ [] for word in sentence]
  assert len(fields) == 1
  krVec=[token[fields[0]] for token in sentence]
  nounCases = [ [] for word in sentence]
  
  #print krVec
  
  for c,kr in enumerate(krVec):
    if 'CAS' not in kr:
    #if 'NOUN' not in kr:
      continue
    cases=casCode.findall(kr)
    if cases == []:
      nounCases[c]=['NO_CASE']  
    else:
      case = cases[0][-4:-1]
      nounCases[c]=[case]
  
  
  #print nounCases
  
  leftCase={}
  rightCase={}
  
  currCase=None
  casePos=None
  for i in range( len(sentence) ):
    if nounCases[i]==[]:
      leftCase[i]=(currCase, casePos)
    else:
      currCase = nounCases[i]
      casePos = i
      leftCase[i]=(None, None)
   
  #print leftCase
  
  currCase=None 
  casePos=None
  for i in range( len(sentence)-1, -1, -1):
    if nounCases[i]==[]:
      rightCase[i]=(currCase, casePos)
    else:
      currCase = nounCases[i]
      rightCase[i]=(None, None)
      casePos = i
    
  #print rightCase
  
  for i in range ( len(sentence) ):
    if rightCase[i][0]==leftCase[i][0] and rightCase[i][0]!=None:
      if abs(rightCase[i][1]-leftCase[i][1])<=maxDist:
        featVec[i]=[1]
        continue

    featVec[i]=[0]
    
  return featVec            
  
def getPosTag(kr):
  if '/' in kr:
    return getPosTag(kr.split('/')[-1])
  else:
    return nonalf.split(kr)[0]

def krPatts(sen, fields, options, fullKr=False):
  lang = options['lang']
  assert lang in ('en', 'hu')
  minLength = options['minLength']
  maxLength = options['maxLength']
  rad = options['rad']
  
  assert len(fields)==1
  f = fields[0]
  featVec = [ [] for tok in sen]
  krVec = [tok[f] for tok in sen]
  if lang == 'hu':
    if not fullKr:
      krVec = [getPosTag(kr) for kr in krVec] 
  else:
    krVec = [tok[f][0] for tok in sen]
  
  assert len(krVec) == len(sen)
  #sys.stderr.write(str(len(sen))+'words\n')
  for c in range(len(krVec)):
    #sys.stderr.write('word '+str(c)+'\n')
    for i in range (-rad, rad):
      for j in range(-rad+1, rad+2):
        #sys.stderr.write(str(i)+' '+str(j))
        a = c+i
        b = c+j
        
        #if b-a == 3:
        #sys.stderr.write(str(c)+'\t'+str(i)+' '+str(j)+'\n')
        
        if a >= 0 and b <= len(krVec) and b-a >= minLength and b-a <= maxLength:
          #sys.stderr.write('*')
          value = '+'.join([ krVec[x] for x in range(c+i, c+j) ])
          feat = '_'.join( (str(i), str(j), value) )
          featVec[c].append(feat)
        #sys.stderr.write('\n')
  return featVec 

def parsePatts(sen, fields, options, fullKr=False):
  minLength = options['minLength']
  maxLength = options['maxLength']
  rad = options['rad']
  
  assert len(fields)==1
  f = fields[0]
  featVec = [ [] for tok in sen]
  krVec = [tok[f] for tok in sen]
  
  assert len(krVec) == len(sen)
  #sys.stderr.write(str(len(sen))+'words\n')
  for c in range(len(krVec)):
    #sys.stderr.write('word '+str(c)+'\n')
    for i in range (-rad, rad):
      for j in range(-rad+1, rad+2):
        #sys.stderr.write(str(i)+' '+str(j))
        a = c+i
        b = c+j
        
        #if b-a == 3:
        #sys.stderr.write(str(c)+'\t'+str(i)+' '+str(j)+'\n')
        
        if a >= 0 and b <= len(krVec) and b-a >= minLength and b-a <= maxLength:
          #sys.stderr.write('*')
          value = '+'.join([ krVec[x] for x in range(c+i, c+j) ])
          feat = '_'.join( (str(i), str(j), value) )
          featVec[c].append(feat)
        #sys.stderr.write('\n')
  return featVec 


def getTagType(tag):
  return tag[2:]

def posStart(postag):
  return postag[0]

def posEnd(postag):
  return postag[-1]

def getNpPart(chunkTag):
  if chunkTag == 'O' or chunkTag[2:]!='NP':
    return 'O'
  else:
    return chunkTag[0]
