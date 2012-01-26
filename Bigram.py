#!/usr/bin/python
import sys
import math

startAndEndTag = "S"
startAndEndObs = "S"


def transprobs(corp, field):
  bg=Bigram(0.00000000001)
  for s in corp:
	w=['S','S','S','S']
	for next in s:
	  bg.obs(w[field],next[field])
	  w=next
	bg.obs(w[field], startAndEndTag)
  bg.count()		  
  return bg

def obsprobs(corp,TField,WField):
  obg=Bigram(0.0000000001)
  for s in corp:
	for w in s:
	  obg.obs(w[TField], w[WField])
  obg.count()
  return obg

class Bigram:
  def __init__(self, smooth):
	self.bigramcount={}
	self.bigramLogProb={}
	self.unigramcount={}
	self.logSmooth=math.log(smooth)
	self.updated=False
	self.updatewarning='WARNING: Probabilities have not been recalculated since last input!'
	self.obscount=0
	self.unigrlogprob={}
  def obs(self, egy, ketto):
	try:
	  self.bigramcount[(egy,ketto)] += 1.0
	except KeyError:
	  self.bigramcount[(egy,ketto)] = 1.0
  
        self.obscount+=1
	self.updated=False
		  
  def count(self):
	for key in self.bigramcount:
	  try:
		self.unigramcount[key[0]] += self.bigramcount[key]
	  except KeyError:
		self.unigramcount[key[0]] = self.bigramcount[key]
  
	for key in self.bigramcount:
	  self.bigramLogProb[key] = math.log( self.bigramcount[key] / self.unigramcount[key[0]] )
	
	
	for tag in self.unigramcount:
            self.unigrlogprob[tag]=math.log(self.unigramcount[tag]/self.obscount)
	
	self.updated=True
	
		
  def unigramlogprob(self, tag):
    return self.unigrlogprob[tag]
  
  def logProb(self, egy, ketto):
	if not self.updated:
	  print self.updatewarning 

	try:
	  return self.bigramLogProb[(egy,ketto)]
	except KeyError:
	  return self.logSmooth
  
  def prob(self, egy, ketto):
	return math.exp(self.logProb(egy,ketto)) 
