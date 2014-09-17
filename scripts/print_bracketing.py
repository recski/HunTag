import sys
in_phrase = False
for line in sys.stdin:
    if line == '\n':
        if in_phrase:
            print ']',
            in_phrase = False
        print
        continue
    tok = line.strip().split()
    word = tok[0]
    part = tok[-1][0]
    if part in ('B', '1'):
        print '[',
        in_phrase = True
    print word,
    if part in ('E', '1'):
        print ']',
        in_phrase = False
