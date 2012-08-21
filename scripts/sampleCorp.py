#!/usr/bin/python
def main(ratio, setOff):
  currSen=[]
  c=0
  for line in sys.stdin:
    if line =='\n':
      printSen(currSen, c, ratio, setOff)
      currSen=[]
    else:
      currSen.append(line)
      c+=1

def printSen(sen, c, ratio, setOff):
  if (c+setOff)%ratio==0:
    for line in sen:
      print line,
    print    
  else:
    for line in sen:
      sys.stderr.write(line)
    sys.stderr.write('\n')

if __name__=='__main__':
  import sys
  try:
    main(int(sys.argv[1]), int(sys.argv[2]))
  except (ValueError, IndexError):
    sys.stderr.write('hibauzenet\n')