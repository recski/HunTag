#!/usr/bin/python
import sys

def log(cucc):
  sys.stderr.write(str(cucc))

def buildMap(infile):
  log('building map...\n')
  map={}
  for line in open(infile):
    feats=line.split()[1:]
    for feat in feats:
      try:
        map[feat]+=1
      except KeyError:
        map[feat]=1
  
  return map

def dumpFeats(infile, map, outfile, featsfile):
  log('writing features...\n')
  out=open(outfile, 'w')
  
  krPattOnly = True
  
  for line in open(infile):
    l=line.split()
    if krPattOnly:
      feats = [feat for feat in l[1:] if map[feat]>=cutoff or 'krpatt' not in feat]
    else:
      feats = [feat for feat in l[1:] if map[feat]>=cutoff]
    
    
    outstring=l[0]+'\t'
    
    
    for feat in feats:
      outstring+=feat+' '
    out.write (outstring[:-1]+'\n')

  log('writing list of kept features')
  fout=open(featsfile,'w')
  for key in map:
    if map[key]>=cutoff:
      fout.write(key+'\n')

if __name__=='__main__':
  
  #testProcess()
  #sys.quit(-1)
  infile = sys.argv[1]
  outfile = sys.argv[2]
  cutoff = int(sys.argv[3])
  featsfile = sys.argv[4]
  
  log('cutoff is '+str(cutoff)+'\n')
  
  map=buildMap(infile)
  dumpFeats(infile, map, outfile, featsfile)
