
# coding: utf-8

# In[15]:

import numpy as np
import math
import matplotlib.pyplot as plt
import random
from numpy.random import rand


# read text

# In[1]:

def read_text_words(filename, wordsnumber):    
    with open(filename) as f:
        for i in xrange(wordsnumber):
            X = f.readlines()
            wordsnumber = len(X)    
    X = ''.join(X) 
    X = X.replace('\n', '{') #123
    return X

def read_text_whole(filename):
    with open(filename) as f:
        X = f.read()    
    X = X.replace('\n', '{') #123
    return X

def chop_text_to_size(text, size):
    return text[:1024*1024*size]

def read_text_filesize(filename, size):
    with open(filename) as f:
        X = f.read(1024*1024*size)
    X = X.replace('\n', '{') #123
    return X    


# counts

# In[3]:

def get_unicount(text):
    length = len(text)
    counts = np.zeros(27)
    for i in xrange(length):
        c = ord(text[i])
        counts[c-97]+=1
        #97-122, 123 - word delimiter    
    return counts[:26]


# bigram statistics

# In[4]:

def get_bigram_stats_dic(text):        
    length = len(text)
    dic = {}
    for i in xrange(length-1):
        if ord(text[i]) == 123 or ord(text[i+1]) == 123:
            continue            
        if (text[i], text[i+1]) in dic:
            dic[(text[i], text[i+1])] += 1
        else: 
            dic[(text[i], text[i+1])] = 1 
            
    for k,v in dic.items():
        r = 0
        if (k[0],'{') in dic.keys():
            r = dic[(k[0],'{')]
        dic[k] = v/(sum(stats))
    return dic


# quality

# In[5]:

def quality(decrypted, original):
    l = len(decrypted)
    zipped = zip(decrypted, original)    
    return sum(1 for x,y in zipped if x != y)/l


# crypt

# In[6]:


def crypt(text):
    p = range(26)
    random.shuffle(p)
    output=''
    p.append(26)
    for ch in text:
            try:
                x = ord(ch) - ord('a')
                output+=(chr(p[x] + ord('a')))
            except:
                pass
    return output, p


# metropolis and density maximization

# In[37]:


# from random import random
"""
This module implements algorithm of Metropolis-Hastings 
for random variable generation.
The algorithm generates random variables from a desired 
distribution (which may be unnormalized).
"""

def metropolis( desiredPDF, initValue, computableRVS, skipIterations = 1 ):
    """
    This function returns a generator, which generates random variables 
    from some space S with a desired distribution using Metropolis-Hastings 
    algorithm.
    
    Args:
        desiredPDF (func) : PDF of desired distribution p( T ), where T from S
        initValue : an object from S to initialize the starting point 
        of iterative proccess
        computableRVS (func) : a generator of random value from space S 
        with given parameter T, which is also from S
        skipIterations (int) : number of iterations to skip 
        (skipping more iterations leads to better accuracy? 
        but greater time consuming)
        
    Returns: generator, which produce some values from S 
    and their denisity according to distribution desiredPDF
    """
    
    random_variable = initValue
    random_variableDensityValue = desiredPDF( random_variable )
    """
    A state of MCMC
    """
    
    #ignore first iterations to let the iterative proccess 
    #converge to some distribution, which is close to desired
    for i in xrange( skipIterations ):
        candidate = computableRVS( random_variable )
        candidateDensityValue = desiredPDF( candidate )
        """
        next candidate for sample, generated by computableRVS
        """
        
#         acceptanceProb = min( 1, candidateDensityValue / random_variableDensityValue )
# logp is returnd by desiredPDF_bigram, so here is the change
        acceptanceProb = min(  0, candidateDensityValue - random_variableDensityValue )
        """
        probability to accept candidate to sample
        """
        
        if random.random() < acceptanceProb:
            random_variable = candidate
            random_variableDensityValue = candidateDensityValue
            
    #now when the procces is converged to desired distribution, 
    #return acceptable candidates
    while True:
        candidate = computableRVS( random_variable )
        candidateDensityValue = desiredPDF( candidate )
        """
        next candidate for sample, generated by computableRVS
        """
        
#         acceptanceProb = min( 1, candidateDensityValue / random_variableDensityValue )
# logp is returnd by desiredPDF_bigram, so here is the change
        acceptanceProb = min( 0, candidateDensityValue - random_variableDensityValue )
        """
        probability to accept candidate to sample
        """
        
        if random.random() < acceptanceProb:
            random_variable = candidate
            random_variableDensityValue = candidateDensityValue
        yield random_variable, random_variableDensityValue

def densityMaximization( desiredPDF, initValue, computableRVS, skipIterations = 200 ):
    """
    This function return a generator, which generates random variables 
    from some space S by trying to maximize givven density. 
    The algorithm is a modification of Metropolis-Hastings. 
    It rejects all objects, which decrease density.
    
    Args:
        desiredPDF (func) : PDF of desired distribution p( T ), where T from S
        initValue : an object from S to initialize the starting point 
        of iterative proccess
        computableRVS (func) : a generator of random value from space S 
        with given parameter T, which is also from S
        skipIterations (int) : number of iterations to skip 
        (skipping more iterations leads to better accuracy? 
        but greater time consuming)
        
    Returns: generator, which produce some values from S, 
    where each next value has no less density, and their denisity
    """
    
    random_variable = initValue
    random_variableDensityValue = desiredPDF( random_variable )
    """
    A state of MCMC
    """
    
    #ignore first iterations to let the iterative proccess to enter 
    #the high density regions
    for i in xrange( skipIterations ):
        candidate = computableRVS( random_variable )
        candidateDensityValue = desiredPDF( candidate )
        """
        next candidate for sample, generated by computableRVS
        """
        
        if random_variableDensityValue < candidateDensityValue:
            random_variable = candidate
            random_variableDensityValue = candidateDensityValue
            
    #now when the procces is in high density regions, 
    #return acceptable candidates
    while True:
        candidate = computableRVS( random_variable )
        candidateDensityValue = desiredPDF( candidate )
        """
        next candidate for sample, generated by computableRVS
        """
        
        if random_variableDensityValue < candidateDensityValue:
            random_variable = candidate
            random_variableDensityValue = candidateDensityValue
        yield random_variable, random_variableDensityValue


# permutation generator and computablervs

# In[8]:

"""
This module provide some functions, 
that generate random permutations with different distributions. 
There are a uniform distribution and a symmetric distribution, 
which depends on some other permutation.
"""

def uniform( n ):
    """
    Generates random permutation using Knuth algorithm.
    
    Args:
        n (int) : length of permutation
        
    Returns: random permutation of length n from uniform distribution
    """
    
    #initialize permutation with identical
    permutation = [ i for i in xrange( n ) ]
    
    #swap ith object with random onject from i to n - 1 enclusively
    for i in xrange( n ):
        j = random.randint( i, n - 1 )
        permutation[ i ], permutation[ j ] = permutation[ j ], permutation[ i ]
        
    permutation.append(26)
    
    return permutation

def applyedTranspostions( basePermutation ):
    """
    This function returns random permutation by applying random 
	transpositions to given permutation.
    
    The result distribution is not uniform and 
	symmetric assuming parameter.
    
    Args:
        basePermutation (array) : parameter of distribution
        
    Returns: random permutation generated from basePermutation
    """
    
    n = len( basePermutation) -1
    """
    length of permutation
    """
    
    #apply n random transpositions (including identical) to base permutation
    for i in xrange( n ):
        k, l = random.randint( 0, n - 2 ), random.randint( 0, n - 2 )
        basePermutation[ k ], basePermutation[ l ] = basePermutation[ l ],        basePermutation[ k ]
        
    return  basePermutation


# desiredPDF

# In[19]:

def get_desiredPDF_bigram(permutation):
    logp = 0
    for i in xrange(len(encrypted)-1):
        if (chr(permutation[ord(encrypted[i])-97]+97), 
            chr(permutation[ord(encrypted[i+1])-97]+97)) in stats.keys():
            logp += math.log(stats[(chr(permutation[ord(encrypted[i])-97]+97), 
                               chr(permutation[ord(encrypted[i+1])-97]+97))]) 
    return logp


## Varying training text size

# Fix large (e.g. 5000 or more words) encrypted text and explore how the ratio of correctly decrypted symbols
# depends on the size of training text (using the same number of MCMC iterations)

### Encryption

# In[ ]:

fname = 'main/oliver_twist.txt'
test_text = read_text_words(fname, 5000)
encrypted = crypt(original)
print encrypted[:20]


### Metropolis

# In[ ]:

sizes =  [2,4,8,16]
for s in sizes:   
    i=0
    train_text = read_text_filesize('main/super.txt', s)
    counts = get_unicount(train_text)
    bistats = get_bigram_stats_dic(train_text)
#     print chr(np.argmax(counts)+97)
#     print max(bistats.iteritems(), key=operator.itemgetter(1))[0]
    
    #Metropolis here
    #decryption
    #output - decrypted text
#     qs = np.zeros(len(sizes))
#     qs[i] = quality(decrypted, original)
#     i+=1

print train_text[:1000]
# plt.plot(sizes, qs) 


## TO BE DELETED

# In[13]:

#TEST TEXT
fname = 'main/oliver_twist.txt'
original = read_text_words(fname, 1000)
encrypted, p = crypt(original)

#TRAIN TEXT
length = 575514
train_text = read_text_words('main/war_and_peace.txt', length)
counts = get_unicount(train_text)
stats = get_bigram_stats_dic(train_text)
print p


# In[35]:

computableGen = lambda t: applyedTranspostions(t)
init_p = uniform(26)
metropolisgenerator =     metropolis(get_desiredPDF_bigram, init_p, computableGen )
#     densityMaximization(get_desiredPDF_bigram, init_p, computableGen )
x = []
for i in xrange( 10 ):
    x.append( metropolisgenerator.next()[0] )


# In[36]:

for i in x:
    print i


# In[30]:

per = x[0]
for i in xrange(len(per)):
    print (ord('a') + i) == (ord('a') + per[p[i]])


# In[ ]:



