
# coding: utf-8

# In[1]:


import re
from collections import defaultdict, Counter
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
stop_words = set(stopwords.words("english"))


# In[2]:


def words(text): return re.findall(r'\w+', text.lower())
def wnTag(pos): return {'noun': 'n', 'verb': 'v', 'adjective': 'a', 'adverb': 'r'}[pos]
TF = defaultdict(lambda: defaultdict(lambda: 0))
DF = defaultdict(lambda: [])


# In[3]:


def leskOverlap(senseDef, target):
    wnidCount = [ (wncat, tf, word, len(DF[word])+1) for word in senseDef                                                     for wncat, tf in TF[word].items()                                                     if wncat in target.values() ]
    res = sorted( [ (word, tf*int(2653/df)) for wnid, tf, word, df in wnidCount], key = lambda x: -x[1])[:5]
    feature = {}
    for i in res:
        feature[i[0]] = i[1]
    return feature


# In[4]:


training = [  line.strip().split('\t') for line in open('wn.in.evp.cat.txt', 'r') if line.strip() != '' ]


# In[5]:


len(training)


# In[6]:


def isHead(head, word, tag):
        try:
            return lmtzr.lemmatize(word, tag) == head
        except:
            return False
for wnid, wncat, senseDef, target in training:
        head, pos = wnid.split('-')[:2]
        tokens = [word for word in words(senseDef) if word not in stop_words]
        for word in tokens:
            if word != head and not isHead(head, word, pos):
                TF[word][wncat] += 1
                DF[word] += [] if wncat in DF[word] else [wncat] 


# In[7]:


Class = []
features = []
for wnid, wncat, senseDef, target in training:
    tokens = [word for word in words(senseDef) if word not in stop_words]
    Class.append(eval(target))
    features.append((leskOverlap(tokens, eval(target)),wncat))


# In[8]:


features[0]


# In[9]:


train_set,test_set,train_class,test_class = train_test_split(features,Class,test_size=0.1, random_state=42)


# In[10]:


train_set[1]


# In[11]:


print(len(train_set))
print(len(test_set))
print(len(train_class))
print(len(test_class))


# In[ ]:


from nltk.classify import SklearnClassifier 
from sklearn.linear_model import LogisticRegression
classifier = SklearnClassifier(LogisticRegression(C=10e5)).train(train_set)


# In[ ]:


print(nltk.classify.accuracy(classifier, test_set))


# In[ ]:


hits =0
for i in range(len(test_set)):
    prob_d = sklearn_classifier.prob_classify(test_set[i][0])._prob_dict
    corr = test_set[i][1]
    maxx = max(test_class[i].values(),key=lambda x: prob_d.get(x, 0))
    if corr == maxx:
        hits +=1


# In[ ]:


print('第一種未塞選方法',nltk.classify.accuracy(classifier, test_set))
print('第二種塞選後方法',hits/len(test_class))


# In[ ]:


get_ipython().system('jupyter nbconvert --to script Lab5_106065503.ipynb')

