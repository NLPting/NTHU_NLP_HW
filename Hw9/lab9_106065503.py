
# coding: utf-8

# In[1]:


import sys
from akl import akl
from collections import defaultdict


# In[2]:


pgPreps = 'in_favor_of|_|about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|towarV in favour of	ruled in favour ofV in favour of	ruled in favour ofds|with'.split('|')
otherPreps ='out|down'.split('|')
verbpat = ('V; V n; V ord; V oneself; V adj; V -ing; V to v; V v; V that; V wh; V wh to v; V quote; '+              'V so; V not; V as if; V as though; V someway; V together; V as adj; V as to wh; V by amount; '+              'V amount; V by -ing; V in favour of n; V in favour of ing; V n in favour of n; V n in favour of ing; V n n; V n adj; V n -ing; V n to v; V n v n; V n that; '+              'V n wh; V n wh to v; V n quote; V n v-ed; V n someway; V n with together; '+              'V n as adj; V n into -ing; V adv; V and v').split('; ')
verbpat += ['V %s n' % prep for prep in pgPreps]+['V n %s n' % prep for prep in verbpat]
verbpat += [pat.replace('V ', 'V-ed ') for pat in verbpat]

pgNoun = ('N for n to v; N from n that; N from n to v; N from n for n; N in favor of; N in favour of; '+            'N of amount; N of n as n; N of n to n; N of n with n; N on n for n; N on n to v'+            'N that; N to v; N to n that; N to n to v; N with n for n; N with n that; N with n to v').split('; ')
pgNoun += pgNoun + ['N %s -ing' % prep for prep in pgPreps ]
pgNoun += pgNoun + ['ADJ %s n' % prep for prep in pgPreps if prep != 'of']+ ['N %s -ing' % prep for prep in pgPreps]
pgAdj = ('ADJ adj; ADJ and adj; ADJ as to wh; '+        'ADJ enough; ADJ enough for n; ADJ enough for n to v; ADJ enough n; '+        'ADJ enough n for n; ADJ enough n for n to v; ADJ enough n that; ADJ enough to v; '+        'ADJ for n to v; ADJ from n to n; ADJ in color; ADJ -ing; '+        'ADJ in n as n; ADJ in n from n; ADJ in n to n; ADJ in n with n; ADJ in n as n; ADJ n for n'+        'ADJ n to v; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing'+        'ADJ wh; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing').split('; ')
pgAdj += [ 'ADJ %s n'%prep for prep in pgPreps ]
pgPatterns = verbpat + pgAdj + pgNoun

reservedWords = 'how wh; who wh; what wh; when wh; someway someway; together together; that that'.split('; ')
pronOBJ = ['me', 'us', 'you', 'him', 'them']


# In[3]:


mapHead = dict( [('H-NP', 'N'), ('H-VP', 'V'), ('H-ADJP', 'ADJ'), ('H-ADVP', 'ADV'), ('H-VB', 'V')] )
mapRest = dict( [('VBG', 'ing'), ('VBD', 'v-ed'), ('VBN', 'v-ed'), ('VB', 'v'), ('NN', 'n'), ('NNS', 'n'), ('JJ', 'adj'), ('RB', 'adv')] )
mapRW = dict( [ pair.split() for pair in reservedWords ] )


# In[4]:


def isPat(pat):
    return pat in pgPatterns


# In[5]:


maxDegree = 9
def sentence_to_ngram(words, lemmas, tags, chunks): 
    return [ (k, k+degree) for k in range(1,len(words)) for degree in range(2, min(maxDegree, len(words)-k+1)) ]


# In[6]:


def hasTwoObjs(tag, chunk):
    if chunk[-1] != 'H-NP': return False
    return (len(tag) > 1 and tag[0] in pronOBJ) or (len(tag) > 1 and 'DT' in tag[1:])


# In[7]:


def chunk_to_element(words, lemmas, tags, chunks, i, isHead):
    if isHead:                                                          
        return mapHead[chunks[i][-1]] if chunks[i][-1] in mapHead else '*'
    
    if lemmas[i][0] == 'favour' and words[i-1][-1]=='in' and words[i+1][0]=='of': 
        return 'favour'
    
    if tags[i][-1] == 'RP' and tags[i-1][-1][:2] == 'VB':                
        return '_'
    
    if tags[i][0][0]=='W' and lemmas[i][-1] in mapRW:                    
        return mapRW[lemmas[i][-1]]
    
    if hasTwoObjs(tags[i], chunks[i]):                                              
        return 'n n'
    
    if tags[i][-1] in mapRest:                            
        return mapRest[tags[i][-1]]
    if tags[i][-1][:2] in mapRest:                        
        return mapRest[tags[i][-1][:2]]
    
    if chunks[i][-1] in mapHead:                            
        return mapHead[chunks[i][-1]].lower()
    
    if lemmas[i][-1] in pgPreps:                                         
        return lemmas[i][-1]
    
    return lemmas[i][-1] 


# In[8]:


def simplifyPat(pat): 
    if pat == 'V ,':   return 'V'
    elif pat == 'N ,': return 'N'
    else: return pat.replace(' _', '').replace('_', ' ').replace('  ', ' ')


# In[9]:


def ngram_to_pat(words, lemmas, tags, chunks, start, end):
    pat, doneHead = [], False
    
    for i in range(start, end):
        isHead = tags[i][-1][0] in ['V', 'N', 'J'] and not doneHead 
        pat.append( chunk_to_element(words, lemmas, tags, chunks, i, isHead) )
        
        if isHead: doneHead = True

    pat = simplifyPat(' '.join(pat))
    return pat if isPat(pat) else ''


# In[10]:


def ngram_to_head(words, lemmas, tags, chunks, start, end):
    for i in range(start, end):
        if tags[i][-1][0] in 'V' and tags[i+1][-1]=='RP':  
            return lemmas[i][-1].upper()+ ('_'+lemmas[i+1][-1].upper())
        if tags[i][-1][0] in ['V', 'N', 'J']:  
            return lemmas[i][-1].upper()


# In[12]:


datas = open('UM-Corpus.en.200k.tagged.txt','r').readlines()


# In[13]:


tmp_patern = []
for line in datas:
    parse = eval(line.strip())
    parse = [ [y.split() for y in x]  for x in parse ]  
    sent = ' '.join([' '.join(x) for x in parse[0] ])
    #print ('\n' + sent)
    tmp = []
    for start, end in sentence_to_ngram(*parse): 
        pat = ngram_to_pat(*parse, start, end)
        if pat:
            pos = pat.split(' ')[0]
            head = ngram_to_head(*parse, start, end)
            if (head+'-'+pos).lower() in akl:
                tmp.append((head+'-'+pos, pat, sent))
    tmp_patern.append((sent,tmp))
                ##print ('%s\t%s\t%s' % (head+'-'+pos, pat, sent))


# In[14]:


from collections import Counter, defaultdict
import numpy as np
import re


# In[15]:


counts = defaultdict(Counter)
sents = defaultdict(lambda: defaultdict(lambda: []))


# In[16]:


for tgt in tmp_patern:
    if tgt[1]:
        for p in tgt[1]:
            #print(p)
            head , patt , sent = p[0] , p[1] , p[2]
            counts[head][patt] += 1
            sents[head][patt].append(sent)


# In[18]:


HiFreWords = open('HiFreWords', 'r').read().split('\t')
Prons = open('prons.txt', 'r').read().split('\n')


# In[19]:


def tokens(str1): return re.findall('[a-z]+', str1.lower()) 


# In[20]:


def getHighCounts(key, ngrams):
    new_counts = list(map(lambda pair: (pair[0], pair[1] * (len(pair[0].split(' '))**1.5)), ngrams.items()))
    values = list(map(lambda x: x[1], new_counts))
    total, avg, std = np.sum(values), np.mean(values), np.std(values)
    remains = filter(lambda pair: pair[1] > avg+std, new_counts)
    return remains


# In[21]:


def score(head, sent):
    tks = tokens(sent)
    bad = sum([t not in HiFreWords and t in Prons for t in tks])
    return -bad


# In[22]:


target = ['ABILITY-N','VALUE-N','DISCUSS-V','FAVOUR-V','CLASSIFY-V','CERTAIN-ADJ']
for head, ngrams in counts.items():
    if head not in target:
        continue
    remains = getHighCounts(head, ngrams)

    print(head.lower())
    for ptn, ctn in remains:
        h_s = max([ (sent, score(head, sent)) for sent in sents[head][ptn] ], key=lambda x: x[1])[0]
        print("%s\t(%s)\t%s"%(ptn, str(counts[head][ptn]), highest_sent))
    print()


# In[ ]:


jupyter nbconvert --to script lab9_106065503.ipynb

