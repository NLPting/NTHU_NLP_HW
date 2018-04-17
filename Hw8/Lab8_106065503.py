
# coding: utf-8

# In[1]:


import sys
from collections import defaultdict
from pprint import pprint
from collections import Counter, defaultdict
#from pgrules import isverbpat
pgPreps = 'in_favor_of|_|about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|towarV in favour of	ruled in favour ofV in favour of	ruled in favour ofds|with'.split('|')
otherPreps ='out|down'.split('|')
verbpat = ('V; V n; V ord; V oneself; V adj; V -ing; V to v; V v; V that; V wh; V wh to v; V quote; '+              'V so; V not; V as if; V as though; V someway; V together; V as adj; V as to wh; V by amount; '+              'V amount; V by -ing; V in favour of n; V in favour of ing; V n in favour of n; V n in favour of ing; V n n; V n adj; V n -ing; V n to v; V n v n; V n that; '+              'V n wh; V n wh to v; V n quote; V n v-ed; V n someway; V n with together; '+              'V n as adj; V n into -ing; V adv; V and v').split('; ')
verbpat += ['V %s n' % prep for prep in pgPreps]+['V n %s n' % prep for prep in verbpat]
verbpat += [pat.replace('V ', 'V-ed ') for pat in verbpat]
reservedWords = 'how wh; who wh; what wh; when wh; someway someway; together together; that that'.split('; ')
pronOBJ = ['me', 'us', 'you', 'him', 'them']

def isverbpat(pat):
    return  pat in verbpat

maxDegree = 9

def sentence_to_ngram(words, lemmas, tags, chunks): 
    return [ (k, k+degree) for k in range(1,len(words)) for degree in range(2, min(maxDegree, len(words)-k+1)) ]
    #                 if chunks[k][-1] in ['H-VP', 'H-NP', 'H-ADJP'] 
    #                 and chunks[k+degree-1][-1] in ['H-VP', 'H-NP', 'H-ADJP', 'H-ADVP'] ]

mapHead = dict( [('H-NP', 'N'), ('H-VP', 'V'), ('H-ADJP', 'ADJ'), ('H-ADVP', 'ADV'), ('H-VB', 'V')] )
#mapRest = dict( [('H-NP', 'n'), ('H-VP', 'v'), ('H-TO', 'to'), ('H-ADJ', 'adj'), ('H-ADV', 'adv')] )
mapRest = dict( [('VBG', 'ing'), ('VBD', 'v-ed'), ('VBN', 'v-ed'), ('VB', 'v'), ('NN', 'n'), ('NNS', 'n'), ('JJ', 'adj'), ('RB', 'adv'),
                    ] )

mapRW = dict( [ pair.split() for pair in reservedWords ] )

def hasTwoObjs(tag, chunk):
    if chunk[-1] != 'H-NP': return False
    return (len(tag) > 1 and tag[0] in pronOBJ) or (len(tag) > 1 and 'DT' in tag[1:])
    
def chunk_to_element(words, lemmas, tags, chunks, i, isHead):
    #print ('***', i, words[i], lemmas[i], tags[i], chunks[i], isHead, tags[i][-1] == 'RP' and tags[i-1][-1][:2] == 'VB')
    if isHead:                                                          return mapHead[chunks[i][-1]] if chunks[i][-1] in mapHead else '*'
    if lemmas[i][0] == 'favour' and words[i-1][-1]=='in' and words[i+1][0]=='of': return 'favour'
    if tags[i][-1] == 'RP' and tags[i-1][-1][:2] == 'VB':                return '_'
    if tags[i][0][0]=='W' and lemmas[i][-1] in mapRW:                    return mapRW[lemmas[i][-1]]
    if hasTwoObjs(tags[i], chunks[i]):                                              return 'n n'
    if tags[i][-1] in mapRest:                            return mapRest[tags[i][-1]]
    if tags[i][-1][:2] in mapRest:                        return mapRest[tags[i][-1][:2]]
    if chunks[i][-1] in mapHead:                            return mapHead[chunks[i][-1]].lower()
    if lemmas[i][-1] in pgPreps:                                         return lemmas[i][-1]
    return lemmas[i][-1]

def simplifyPat(pat): return 'V' if pat == 'V ,' else pat.replace(' _', '').replace('_', ' ').replace('  ', ' ')
    
def ngram_to_pat(words, lemmas, tags, chunks, start, end):
    pat, doneHead = [], False
    for i in range(start, end):
        isHead = tags[i][-1][0] in 'V' and not doneHead
        pat.append( chunk_to_element(words, lemmas, tags, chunks, i, isHead) )
        if isHead: doneHead = True
    pat = simplifyPat(' '.join(pat))
    #print ('===', start, end, pat, words[start:end])
    return pat if isverbpat(pat) else ''

def ngram_to_head(words, lemmas, tags, chunks, start, end):
    for i in range(start, end):
        if tags[i][-1][0] in 'V' and tags[i+1][-1]=='RP':  return lemmas[i][-1].upper()+ ('_'+lemmas[i+1][-1].upper())
        if tags[i][-1][0] in 'V':  return lemmas[i][-1].upper()


# In[2]:


tmp_false = []
for line in open('ef_train.src.tagged.txt','r').readlines():
    parse = eval(line.strip())
    parse = [ [y.split() for y in x]  for x in parse ]
    tmp = []
    sentence = '\n'+' '.join([' '.join(x) for x in parse[0] ])
    #print (sentence)
    for start, end in sentence_to_ngram(*parse):
        pat = ngram_to_pat(*parse, start, end)
        if pat: 
            #print ('%s\t%s\t%s' %(ngram_to_head(*parse, start, end), pat, ' '.join([' '.join(x) for x in parse[0][start:end] ]) ))
            tmp.append((ngram_to_head(*parse, start, end), pat, ' '.join([' '.join(x) for x in parse[0][start:end] ]) ))
    tmp_false.append((sentence,tmp))


# In[3]:


tmp_correct = []
for line in open('ef_train.tgt.tagged.txt','r').readlines():
    #if "'out', 'in', 'favour', 'of'," not in line and "'down', 'in', 'favour', 'of'," not in line: continue
    parse = eval(line.strip())
    parse = [ [y.split() for y in x]  for x in parse ]
    
    tmp = []
    sentence = '\n'+' '.join([' '.join(x) for x in parse[0] ])
    #print (sentence)
    for start, end in sentence_to_ngram(*parse):
        pat = ngram_to_pat(*parse, start, end)
        if pat: 
            #print ('%s\t%s\t%s' %(ngram_to_head(*parse, start, end), pat, ' '.join([' '.join(x) for x in parse[0][start:end] ]) ))
            tmp.append((ngram_to_head(*parse, start, end), pat, ' '.join([' '.join(x) for x in parse[0][start:end] ]) ))
    tmp_correct.append((sentence,tmp))


# In[4]:


N_M = defaultdict(Counter)
L_M = defaultdict(Counter)


# In[5]:


for false,correct in zip(tmp_false,tmp_correct):
    f = [(item[0],item[1])for item in false[1]]
    c = [(item[0],item[1])for item in correct[1]]
    for f_head,f_tag in f:
        for c_head,c_tag in c:
            L_M[c_head][c_tag]+=1
            if f_head==c_head and f_tag!=c_tag:
                N_M[f_tag][c_tag]+=1
    
    


# In[6]:


tmp_test = []
for line in open('ef_test.src.tagged.txt','r').readlines():
    parse = eval(line.strip())
    parse = [ [y.split() for y in x]  for x in parse ]
    
    tmp = []
    sentence = '\n'+' '.join([' '.join(x) for x in parse[0] ])
    #print (sentence)
    for start, end in sentence_to_ngram(*parse):
        pat = ngram_to_pat(*parse, start, end)
        if pat: 
            tmp.append((ngram_to_head(*parse, start, end), pat, ' '.join([' '.join(x) for x in parse[0][start:end] ]) ))
            #print ('%s\t%s\t%s' %(ngram_to_head(*parse, start, end), pat, ' '.join([' '.join(x) for x in parse[0][start:end] ]) ))
    tmp_test.append((sentence,tmp))


# In[7]:


tmp_result = []
for line in open('ef_test.ref.txt','r').readlines():
    l = line.split('\t')
    result = (l[-2],l[-1].strip())
    tmp_result.append(result)


# In[8]:


tmp_result[0]


# In[9]:


for index , test in enumerate(tmp_test):
    t_sentence = test[0].strip()
    t = [(item[0],item[1])for item in test[1]]
    print(t_sentence)
    for head,tag in t:
        if head not in ['DISCUSS', 'ANSWER', 'APPLY', 'EXPLAIN']: continue
        option =[(c_patern,N_M[tag][c_patern] / sum(N_M[tag].values()) * L_M[head][c_patern] / sum(L_M[head].values())) for c_patern in N_M[tag]]
        print('Model : ', head , tag , str('------>') , max(option,key = lambda x : x[1]))
        print('Answer : ', tmp_result[index][0] , tmp_result[index][1])
        print('\n')
        
    
        
        
        
        

