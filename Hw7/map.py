from collections import defaultdict, Counter
import fileinput
import sys
import re
from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english')) 
max_distance = 5

coll = defaultdict(lambda: 0)
def tokens(str1): return re.findall('[a-z]+', str1.lower())

def ngrams(sent, n):
    return [ ' '.join(x) for x in zip(*[sent[i:] for i in range(n) if i <= len(sent) ] ) ]

for ii in open('bnc.coll.small.txt','r').readlines():
    token = ii.split('\t')
    partten = ' '.join(token[:2])
    value = int(token[-2])
    coll[partten] = value
    
lines = []
for sen in fileinput.input():
#for sen in open('bnc.sents.txt').readlines():
    sent = tokens(sen)
    if 10<=len(sent)<=25:
        tmp = []
        for n in range(2,6):
            for ngram in ngrams(sent,n):
                token = ngram.split(' ')
                head = token[0]
                tail = token[-1]
                tmp.append(head+' '+ tail)
                tmp.append(tail+ ' '+ head)  
        for i in tmp:
            if coll[i]:
                print(i+' '+str(coll[i])+'\t'+sen)
                #lines.append(i+' '+str(coll[i])+'\t'+sen)