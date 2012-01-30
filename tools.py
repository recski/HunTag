
def sentenceIterator(input):
  currSen = []
  for line in input:
    if line == '\n' and currSen!=[]:
      yield currSen
      currSen = []
      continue
    currSen.append(line.strip().split())
  if currSen!=[]:
    yield currSen
  return

def writeSentence(sen):
  for tok in sen:
    print '\t'.join(tok)
  print
