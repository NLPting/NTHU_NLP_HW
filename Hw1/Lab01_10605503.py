
# coding: utf-8

# In[34]:


import re
import re, collections


# In[40]:


def words(text): return re.findall(r'\w+', text.lower())

def words_and_bigrams(text):
    all_words = words(text)
    bigrams=[]
    for i in range(len(all_words)-1):
        bigrams.append(' '.join(all_words[i:i+2]))
    return all_words + bigrams

def b_model(word_set):
    model = collections.defaultdict(lambda: 1)
    for word in word_set:
        model[word]+=1
    return model


# In[223]:


B_WORD = b_model(words_and_bigrams(open('big.txt').read()))


# In[224]:


def P(word, N=sum(B_WORD.values())): 
    "Probability of `word`."
    return B_WORD[word] / N

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in B_WORD)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def fusion(word):
    word = word.replace(' ', '')
    splits  = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    wordd = []
    for a,b in splits:
        if a in B_WORD and b in B_WORD:
            wordd.append(a+' '+b)
    return wordd+[word]


def correct(word):
    candidates = known([word]) or known(edits1(word)) or known(edits2(word)) or [word]
    #print(candidates)
    fusions = fusion(word)
    #print(fusions)
    if fusions:
        return max(fusions, key=P)
    return max(candidates, key=P)

    

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


# In[235]:


print(correct('taketo'))
print(correct('mor efun'))
print(correct('with out'))

