from pprint import pprint
import re, collections
MAXBEAM = 500
letters = 'abcdefghijklmnopqrstuvwxyz'

def words(text):
    return re.findall(r'([a-z]+|[.,:?!])', text.lower())

word_count = collections.Counter(words(open('big.txt').read()))

def P(word, N = sum(word_count.values())):
    return word_count[word]/N

def next_states(state):
    L, R, edit, prob = state
    R0, R1 = R[0], R[1:]

    if edit == 2:
        return [(L+R0, R1, edit, prob)]
        
    noedit = [(L+R0, R1, edit, prob)]
    delete = [(L, R1, edit+1, P(L+R1))]
    replace = [(L+l, R1, edit+1, P(L+l+R1)) for l in letters]
    insert  = [(L+R0+l, R1, edit+1, P(L+R0+l+R1)) for l in letters]
    
    return noedit + delete + replace + insert



def correction(word):
    states = [ ("", word, 0, P(word)) ]
    for _ in range(len(word)):
        print(states[:3])
        states = [ state for states in map(next_states, states) for state in states ]
        
    ## Combine states with the same L and R   
    D = {}
    for state in states:
        
        words = state[0]+state[1]
        if words not in D:
            D[words] = state
        
    tmp = list(D.values())
    
    ##edit first and then decreasing probability of state
    tmp = sorted(tmp, key=lambda x: x[3], reverse=True)
    tmp = sorted(tmp, key=lambda x: x[2])[:MAXBEAM]
    
    ##Filter STATES and keep only states with #edit==0 or probability>0
    for t in tmp:
        if t[2]!=0 or t[3]<=0:
            del t
    ## #edit>0 and probability>0 then remove the state with #edit==0
    for t in tmp:
        if t[2]==0:
            del t
    
    
    result = sorted(tmp, key=lambda x: x[3], reverse=True)
    return result[:3]


pprint(correction('appearant'))
