#!/usr/bin/python
#eval.py comes with HunTag and is capable of evaluating precision and recall of sequential tagging output. It can also compute various other statistics. When run with the -c option, its operation is identical to the perl script conlleval.pl provided for the ConLL shared tasks chunking and NER-tagging.
import sys
import optfunc
def getChunksFromCorp(taggedFile, goldField, autoField, mode, strict):
    
    goldChunks = getChunksFromColumn(taggedFile, goldField, mode, strict)
    autoChunks = getChunksFromColumn(taggedFile, autoField, mode, strict)
    
    return (goldChunks, autoChunks)

def printError(lineNum):
    print 'illicit tag in line '+str(lineNum)
    
def getChunksFromColumn(taggedFile, field, mode, strict):    
    chunks = []
    chunkStart = None
    chunkType = None
    
    for c,line in enumerate(taggedFile):
        if line=='\n':
            continue
        try:
            tag = line.split()[field]
        except IndexError:
            print
            sys.stderr.write('invalid number of fields in line '+str(c)+'\n'+line)
            sys.exit(-1)
        
        if tag[0] == 'B':
            if strict:
                if mode == 'BIE1':
                    if chunkStart!=None:
                        printError(c)
                        sys.exit(-1)
            
            
            if chunkStart != None:
                chunks.append( (chunkStart, c-1, chunkType) )
                
            chunkStart = c
            chunkType = tag[2:]
            
        elif tag[0]=='I':
            if strict:    
                if chunkStart==None or chunkType!=tag[2:]:
                    printError(c)
                    sys.exit(-1)
        
        elif tag[0]=='E':
            if strict:
                if mode !='BIE1' or chunkStart==None or chunkType!=tag[2:]:
                    printError(c)
                    sys.exit(-1)
            
            if chunkStart==None:
                chunkStart=c
                chunkType=tag[2:]
                
            chunks.append( (chunkStart, c, chunkType) )
            chunkStart=None
            chunkType=None
        
        elif tag[0]=='1':
            if strict:
                if mode!='BIE1':
                    printError(c)
                    sys.exit(-1)
            
            if chunkStart!=None:
                chunks.append( (chunkStart, c-1, chunkType) )
            
            chunks.append( (c, c, tag[2:]) )
            
            chunkStart=None
            chunkType=None
            
        else:
            if strict:
                if tag[0]!='O':
                    printError(c)
                    sys.exit(-1)
                
            if chunkStart==None:
                pass
            
            else:
                if strict:
                    if mode=='BIE1':
                        printError(c)
                        sys.exit(-1)
                
                chunks.append( (chunkStart, c-1, chunkType) )
                chunkStart=None
                chunkType=None
        
        if c == len(taggedFile)-1 and chunkStart!=None:
            chunks.append( (chunkStart, c, chunkType) )
                
    return set(chunks)


def evaluate(chunks):
    type_corr={}
    type_auto={}
    type_gold={}
    
    aCh = chunks[1]
    gCh = chunks[0]
    
    n_goldChunks = len(gCh)
    n_autoChunks = len(aCh)
    
    corr = 0.0
    
    for chunk in aCh:	
        type=chunk[2]
        #if type != 'NP': print chunk
        try:
            type_auto[type]+=1
        except KeyError:
            type_auto[type]=1.0
            
        if chunk in gCh:# or (chunk[0], chunk[1], 'MISC') in gCh:
            corr += 1
            try:
                type_corr[type]+=1
            except KeyError:
                type_corr[type]=1.0
    
        
    
    
    for chunk in gCh:
        type = chunk[2]
        try:
            type_gold[type]+=1
        except KeyError:
            type_gold[type]=1.0
    
    types_gold=[type for type in type_gold]
    types_auto=[type for type in type_auto]
    types = types_gold+types_auto
    
    return (n_goldChunks, n_autoChunks, corr, set(types), type_gold, type_auto, type_corr)

def count(chunkCounts, tokCounts):
    results={}
    n_goldChunks, n_autoChunks, corr, types, type_gold, type_auto, type_corr = chunkCounts
    
    toks, corrToks = tokCounts
    
    results['tokens']=toks
    results['acc']=round(100*(corrToks/toks), 2)
    
    try:
        precision = corr/n_autoChunks
    except ZeroDivisionError:
        precision = 0
    
    try:
        recall = corr/n_goldChunks
    except ZeroDivisionError:
        recall = 0
    
    try:    
        fScore = (2*precision*recall)/(precision+recall)
    except ZeroDivisionError:
        fScore = 0
    
    results['goldPhrases']=n_goldChunks
    results['foundPhrases']=n_autoChunks
    results['corrPhrases']=corr
    results['All']=(100*precision, 100*recall, 100*fScore)
    
    for type in types:
        if type_auto.has_key(type):
        
            c=type_auto[type]
            if type in type_corr:
                prec = 100*(type_corr[type]/c)
                rec = 100*(type_corr[type]/type_gold[type])
                fSc = (2*prec*rec)/(prec+rec)
            
            
                results[type]=(prec,rec,fSc,c)
        
            else:
                results[type]=(0,0,0,c)
            
        else:
            results[type]=(0,0,0,0)
        
    return results
    

def printResults(results):
    tok = results['tokens']
    phras = results['goldPhrases']
    found = results['foundPhrases']
    corr = results['corrPhrases']
    acc = results['acc']
    prec = results['All'][0]
    rec = results['All'][1]
    fb = results['All'][2]
    
    print 'processed %.0f tokens with %.0f phrases;' % (tok, phras),
    print 'found: %.0f phrases; correct: %.0f.\n' % (found, corr),
    
    print 'accuracy: %6.2f%%; precision: %6.2f%%;' % (acc, prec),
    print 'recall: %6.2f%%; FB1: %6.2f' % (rec, fb)
    
    sortedTypes=results.keys()
    sortedTypes.sort()
    
    for type in sortedTypes:
        if type in ('corrPhrases', 'tokens', 'foundPhrases', 'acc', 'All', 'goldPhrases'):
            continue
        
        prec = results[type][0]
        rec = results[type][1]
        fb = results[type][2]
        found = int(results[type][3])
        
        print '%17s:' % (type),
        print 'precision: %6.2f%%;' % prec,
        print 'recall: %6.2f%%;' % rec,
        print 'FB1: %6.2f    %.0f' % (fb, found)

def analyzeErrors(chunks):
    gCh=chunks[0]
    aCh=chunks[1]

    errorTypes={'wrongType':0, 'disjunct':0, 'overlap':0, 'aInG':0, 'gInA':0}
    wrongCategory={}
    for chunk in aCh:
        if chunk in gCh:
            continue
        
        nearest=getNearestChunk(chunk, gCh)
        
        if chunk[2]!=nearest[2]:
            errorTypes['wrongType']+=1
            
            try:
                wrongCategory[(nearest[2], chunk[2])]+=1
            except KeyError:
                wrongCategory[(nearest[2], chunk[2])]=1
            
            continue
                    
        gPos=(nearest[0], nearest[1])
        aPos=(chunk[0], chunk[1])
        
        rel = compareChunks(gPos, aPos)
        errorTypes[rel]+=1        

    allErrors=0
    for type in errorTypes:
        allErrors+=errorTypes[type]
    
    return (errorTypes, allErrors, wrongCategory)

def compareChunks(gPos, aPos):
    if aPos[0] < gPos[0]:
        if aPos[1] < gPos[0]:
            return 'disjunct'
        elif aPos[1] < gPos[1]:
            return 'overlap'
        else:
            return 'gInA'
        
    elif aPos[0]==gPos[0]:
        if aPos[1]>gPos[1]:
            return 'gInA'
        else:
            return 'aInG' 
    
    else:
        if gPos[1] < aPos[0]:
             return 'disjunct'
        elif gPos[1] < aPos[1]:
             return 'overlap'
        else:
             return 'aInG'


def getNearestChunk(chunk, gCh):
    chSum=chunk[0]+chunk[1]
    nearest=None
    bestDist=999
    for currChunk in gCh:
        currSum=currChunk[0]+currChunk[1]
        if abs(currSum-chSum)<bestDist:
            bestDist=abs(currSum-chSum)
            nearest=currChunk

    return nearest

def printErrorTypes(errorTypes):
    for type in errorTypes:
        print type+':\t'+str(errorTypes[type])
    

def getChunkPatterns(taggedFile, goldField, autoField, mode):
    if mode != 'BIE1':
        sys.stderr.write('extracting chunk patterns is currently not available in \'BI\' mode!')
        sys.exit(-1)
    
    
    patternCount={}
    
    prevTags = ('O', 'O')
    pattern=[]
    curr=''
    G=False
    A=False
    for c,l in enumerate(taggedFile):
        if l == '\n':
            if len(pattern)!=0:
                wPatt = ' '.join(pattern)
                #print wPatt
                try:
                    patternCount[wPatt]+=1
                except KeyError:
                    patternCount[wPatt]=1
                
                pattern=[]
            
            continue
            
        line = l.split()
        goldTag = line[goldField][0]
        autoTag = line[autoField][0]

        
    
        if goldTag in ('B', 'E'):
            curr+='g'
            G=False
        elif goldTag == '1':
            curr+='gg'
            G=False
        elif goldTag == 'O':
            if not G:
                curr+='G'
                G = True
        
        else:
            assert goldTag == 'I'
                
        if autoTag in ('B', 'E'):
            curr+='a'
            A=False
        elif autoTag == '1':
            curr+='aa'
            A=False
        elif autoTag == 'O':
            if not A:
                curr+='A'
                A = True
            
        else:
            assert autoTag == 'I' 
            
                        
        if curr not in ('', 'GA'):
            pattern.append(curr)
        
        curr=''
        
        if goldTag==autoTag:
            
            if autoTag in ('I', 'B'):
                pass
                
            else:
                if autoTag == 'O' and pattern==[]:
                    continue
                    
                wPatt = ' '.join(pattern)
                #print wPatt
                try:
                    patternCount[wPatt]+=1
                except KeyError:
                    patternCount[wPatt]=1
                
                pattern=[] 
    
    return patternCount    


def printPatterns(patternCount):
    
    #sys.stderr.write('1')
    
    all = 0.0
    patterns=[]
    
    """
    patternsToAscii = {'ga ga': '---_____---\n---_____---',
                                         'ggaa' : '---_---\n---_---',
                                         'ga g g ga': '---_____---_____---\n---_____________---',
                                         'ga aa ga': '---_______---\n---___|___---',
                                         'ga g g g g ga': '---_____---_____---_____---\n---_____________________---',
                                         'ga a a ga': '---_____________---\n--_____---_____---',
                                         'a g ga':'-------_____---\n---_________---',
                                         'g a ga':'---_________---\n-------_____---'}
    """                                     
    
    for patt in patternCount:
        if patt in ('ga ga', 'ggaa', 'GA'):
            continue
        all+= patternCount[patt]
        patterns.append( (patternCount[patt], patt) )
        
    patterns.sort()
    patterns.reverse()
    for patt in patterns:
        percent = (patternCount[patt[1]]/all)*100
        print str(percent)[:6]+'%\t'+patt[1]+'\n'+patternsToAscii(patt[1])

def patternsToAscii(patt):
    #print patt
    asciiPattG=''
    asciiPattA=''
    for pos in patt.split():
        if 'gg' in pos: 
            asciiPattG+='1'
        elif 'g' in pos:
            asciiPattG+='|'
        
        elif 'G' in pos:
            asciiPattG+=' '
        
        else:    
            asciiPattG+='-'    
            
        if 'aa' in pos: 
            asciiPattA+='1'
        elif 'a' in pos:
            asciiPattA+='|'
        
        elif 'A' in pos:
            asciiPattA+=' '
        
        else:    
            asciiPattA+='-'
        
        
    return asciiPattG+'\n'+asciiPattA    


def countToks(taggedFile, goldField, autoField):
    toks=0.0
    corrToks=0.0
    #print taggedFile
    for line in taggedFile:
        #print '@'
        if line == '\n': continue
        
        toks+=1
        if line.split()[goldField]==line.split()[autoField]:
            corrToks+=1
    
    
    return (toks, corrToks)
    
def printConfMatrix(wrongCategory):
    pairs=wrongCategory.keys()
    pairs.sort()
    for pair in pairs:
        print '%s --> %s %.0f' % (pair[0], pair[1], wrongCategory[pair]) 


def leaveInternalBs(corp):
    newS=True
    newCorp=[]
    for line in corp:
        if line == '\n':
            newCorp.append('\n')
            newS=True
            continue
        else:
            l=line.split()
            newL=l[:-2]
            if l[-2][0]=='B' and not newS:
                newL+=['B'+l[-2][1:]]
            else:
                newL+=['O']
            
            if l[-1][0]=='B' and not newS:
                newL+=['B'+l[-1][1:]]
            else:
                newL+=['O']

            assert len(newL) == len (l)
            newCorp.append('\t'.join(newL))                     
            newS=False
    return newCorp

def getSenPrec(corp):
    allSen=0.0
    corrSen=0.0
    thisSen=True
    for line in corp:
        if line == '\n':
            allSen+=1
            if thisSen:
                corrSen+=1
            thisSen=True
            
        else:
            if line.split()[-2]!=line.split()[-1]:
                thisSen=False
    print 'sentence precision:', str((corrSen/allSen)*100)[:5]+'%'

def runEval(stdin, goldField='-2', autoField='-1', mode='BI', conll=False, bPoints=False, sen=False, strict=False, pattern=False):
    
    """
    try:
        taggedFile = sys.stdin.readlines()
        goldField = int(sys.argv[1])
        autoField = int(sys.argv[2])
        mode = sys.argv[3]
        assert mode in ('BI', 'BIE1')
    except:
        sys.stderr.write( 'usage: eval.py <gold field> <auto field> <mode>\n' )
        sys.exit(-1) 
    """
    
    tF=stdin.readlines()
    chunks = getChunksFromCorp(tF, int(goldField), int(autoField), mode, strict)
    
    chunkCounts = evaluate(chunks)
    #print tF
    tokCounts = countToks(tF, int(goldField), int(autoField))
    #print tokCounts
    results = count(chunkCounts, tokCounts)
    
    #if conll==True:
    if conll==True:
        printResults(results)
        
    if bPoints:
        newCorp=leaveInternalBs(tF)
        #print '\n'.join(newCorp)
        newChunks=getChunksFromCorp(newCorp, int(goldField), int(autoField), 'BI', strict)
        newChunkCounts=evaluate(newChunks)
        newTokCounts=countToks(newCorp, int(goldField), int(autoField))
        newResults = count (newChunkCounts, newTokCounts)
        printResults(newResults)
    #errorTypes, allErrors, wrongCategory=analyzeErrors(chunks)
    #print str(wrongCategory)
    
    if sen:
        getSenPrec(tF)
    
    #assert allErrors+results[2]==results[1]
    #printErrorTypes(errorTypes)
    #printConfMatrix(wrongCategory)
    if pattern:
        patternCount = getChunkPatterns(tF, int(goldField), int(autoField), mode)
    
        printPatterns(patternCount)

def evalInput(input, autoField=-1, goldField=-2):
    inString = ''
    for sen in input:
        for tok in sen:
            inString+='\t'.join(tok)+'\n'
        inString+='\n'
    chunks = getChunksFromCorp(inString, goldField, autoField, 'BI', False)
    chunkCounts = evaluate(chunks)
    tokCounts = countToks(input, goldField, autoField)
    results = count(chunkCounts, tokCounts)
    printResults(results)

if __name__ == '__main__':
    #runEval(sys.stdin, '-2', '-1', 'BIE1', False, True, True, False, False)
    optfunc.run(runEval)
