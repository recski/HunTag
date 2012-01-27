from Lexicon import Lexicon
import sys

from features import *                                                                                                   

class Feature():
  def __init__(self, kind, name, actionName, fields, radius, cutoff, options ) :
    self.name = name
    self.kind = kind
    self.actionName = actionName
    self.fields = fields
    self.radius = radius
    self.cutoff = cutoff
    self.options = options
    if kind=="lex" :
      if self.options != {}:
        sys.stderr.write('Lexicon features do not yet support options')
        sys.exit(-1)
      self.lexicon = Lexicon(actionName)
    elif kind in ("token","sentence") :
      if actionName not in globals() :
        sys.stderr.write( "Unknown operator named "+actionName+"\n" )
	sys.exit(-1)
      self.function = globals()[actionName]
    else :
      assert False

  def evalSentence_Token(self, sentence) :
    featVec = []
    for pos,word in enumerate(sentence) :
      fieldVec = [ word[field] for field in self.fields ]
      if self.options!={}:
        fieldVec += [self.options]
      feat = self.function( *fieldVec )
      featVec.append(feat)
    return featVec

  def evalSentence_Lex(self, sentence) :
    
    assert len(self.fields)==1
    field = self.fields[0]
    
    wordList = [ word[field] for word in sentence ] 
    
    return self.lexicon.lexEvalSentence(wordList)
    
    """
    featVec = []
    assert len(self.fields)==1
    field = self.fields[0]
    for pos,word in enumerate(sentence) :
      form = word[field]
      wf = [ function(form) for function in self.lexicon.functions ]
      wf = [ feat for feat in wf if feat ]
      featVec.append(wf)
    return featVec
    """
    
  def evalSentence_Sentence(self, sentence) :
    if self.options == {}:
      return self.function( sentence, self.fields )    
    else:
      return self.function( sentence, self.fields, self.options )    

  def evalSentence(self, sentence, keepZero) :
    if self.kind=="token" :
      featVec = self.evalSentence_Token(sentence)
    elif self.kind=="lex" :
      featVec = self.evalSentence_Lex(sentence)
    elif self.kind=="sentence" :
      featVec = self.evalSentence_Sentence(sentence)

    multipliedFeatVec = []

    for c,word in enumerate(sentence):
      multipliedFeatVec.append([])
      for i in range (-self.radius, self.radius+1):
        pos = c+i
        if pos<0 or pos>len(sentence)-1 :
	  continue
        
        currentWordFeatures = featVec[pos]
        if not keepZero:
          currentWordFeatures = [feat for feat in currentWordFeatures if feat!=0]
        for feat in currentWordFeatures :
          multipliedFeatVec[c].append(str(i)+'_'+self.name+'='+str(feat))
            
    return multipliedFeatVec

