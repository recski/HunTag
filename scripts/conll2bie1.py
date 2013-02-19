import sys

def conll2bie1(sen):
  tag = sen[0][-1][0]
  for c,tok in enumerate(sen):
    if c == len(sen)-1:
      nextTag = 'O'
    else:
      nextTag = sen[c+1][-1][0]
    
    #sys.stderr.write(tag+'\t'+nextTag+'\t')
      
    if tag == 'B' and nextTag!='I':
      newTag = '1'
    elif tag == 'I' and nextTag!='I':
      newTag = 'E'
    else:
      newTag = tag
    #sys.stderr.write(newTag+'\n')  
    print '\t'.join(tok[:-1]+[newTag+tok[-1][1:]])
    tag = nextTag

def main():
  currSen = []
  for line in sys.stdin:
    if line == '\n':
      conll2bie1(currSen)
      print
      currSen=[]
    else:
      currSen.append(line.strip().split())

if __name__=='__main__':
  main()    