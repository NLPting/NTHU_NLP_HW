from collections import Counter, defaultdict
import math, re
from pprint import pprint
MAXBEAM=500

def words(text): return re.findall(r'\w+', text.lower())
WORDS = Counter(words(open('big.txt').read()))

def Pw(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

count = dict()
C = defaultdict(lambda: 0)
for line in open('count_1edit.txt', 'r', encoding='utf8'):
    wc, num = line.strip().split('\t')
    w, c = wc.split('|')
    count[(w, c)] = int(num)
    C[c] += int(num)

    
Nall = len(count.keys())
N0 = 26*26*26*26+2*26*26*26+26*26-Nall


Nr = []
for i in range(12):
    s=0
    for c in count.items():
        c = c[1]
        if c ==i:
            s=s+1
    Nr.append(s)
Nr[0]=N0

def smooth(count, r=10):
    if count <= r:
        return (count+1)*Nr[count+1] / Nr[count]
    else:
        return count

def Pedit(w, c):
    if (w, c) not in count and C[c] > 0:
        return smooth(0) / C[c]
    if C[c] > 0:
        return smooth(count[(w, c)]) / C[c]
    else:
        return 0
    
def P(pw, pedit):
    return pw*pedit


def next_states(state):
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    L, R, edit, pw, pedit = state
    R0, R1 = R[0], R[1:]
    if edit == 2: return [(L+R0,R1,edit,pw,pedit*0.8)]
    noedit    = [(L+R0,R1,edit,pw,pedit*0.8 )]
    delete    = [(L,R1,edit+1,Pw(L+R1),pedit*Pedit(L[-1]+R0, L[-1]))]  if len(L) > 0 else []
    insert    = [(L+R0+c,R1,edit+1,Pw(L+R0+c+R1),pedit*Pedit(R0,R0+c)) for c in letters]
    replace   = [(L+c,R1,edit+1,Pw(L + c + R1), pedit * Pedit(R0,c)) for c in letters]
    transpose = [(L[:-1] +R0,L[-1]+R1,edit+1,Pw(L[:-1]+R0+L[-1]+R1),pedit*Pedit(L[-1]+R0,R0+L[-1]))] if len(L) > 1 else []
    return set(noedit + delete + replace + insert + transpose)


def correction(word): 
    "Most probable spelling correction for word."
    states = [ ('', word, 0, Pw(word), 1) ]
    for _ in range(len(word)):
        print(states[:3])
        states = [ state for states in map(next_states, states) for state in states ] 

    D = {}
    for state in states:
        words = state[0]+state[1]
        if words not in D:
            D[words] = state
        if state[2] < D[words][2]:
            D[words]=state
            
    tmp = list(D.values())
    tmp = sorted(tmp,key=lambda x: x[2])
    tmp = sorted(tmp, key=lambda x: P(x[3],x[4]), reverse=True)[:MAXBEAM]

    ##Filter STATES and keep only states with #edit==0 or probability>0
    for t in tmp:
        if t[2]!=0 or t[3]<=0:
            del t
    ## #edit>0 and probability>0 then remove the state with #edit==0
    for t in tmp:
        if t[2]==0:
            del t  
    result = sorted(tmp, key=lambda x: P(x[3],x[4]), reverse=True)[:MAXBEAM]
    return result[:3]

pprint(correction('appearant'))