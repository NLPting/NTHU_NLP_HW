from collections import defaultdict, Counter
import sys
import fileinput
import re
from nltk.corpus import stopwords
import operator

eng_stopwords = set(stopwords.words('english')) 
max_distance = 5
def tokens(str1): return re.findall('[a-z]+', str1.lower())

coll_sen = defaultdict(list)

for line in fileinput.input():
    token = line.split('\t')
    partten = token[0]
    sentence = token[1]
    coll_sen[partten].append(sentence)
    

    
Higf = open('HiFreWords','r').read().split('\t')
Prons = open('prons.txt','r').read().split('\n')



for key,sentence in coll_sen.items():
    #print(key)
    tmp = []
    for sen in sentence:
        score = 0
        tok = tokens(sen)
        for word in tok:
            if word not in Higf:
                score += 1
            if word not in Prons:
                score +=1
        tmp.append((sen,score))
        
    result = dict(tmp)
    print(key+'\t'+max(result.items(), key=operator.itemgetter(1))[0])