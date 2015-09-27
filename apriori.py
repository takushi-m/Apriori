import sys,csv
from itertools import chain,combinations
from optparse import OptionParser

def apriori_gen(L,k):
    C = []
    # join step
    for l1 in L:
        for l2 in L:
            if len(l1[0]&l2[0])==k-1:
                C.append(l1[0]|l2[0])

    # prune step
    ret = []
    for c in C:
        isInclude = False
        for sub in combinations(c,k):
            for l in L:
                if sub==l[0]:
                    isInclude = True
        if (not isInclude) and ([c,0] not in ret):
            ret.append([c,0])

    return ret

def apriori_next(D,L,k,minsup):
    C = apriori_gen(L,k)
    for t in D:
        for c in C:
            if c[0].issubset(t):
                c[1] += 1
    ret = []
    for c in C:
        if c[1]>=minsup:
            ret.append(c)
    return ret

def apriori(D,minsup):
    I = [] # items
    for t in D:
        for i in t:
            if i not in I:
                I.append(i)
    I.sort()

    L1 = []
    for i in I:
        cnt = 0
        for t in D:
            if i in t:
                cnt += 1
        if cnt>=minsup:
            L1.append([set([i]),cnt])

    ret = []
    L = L1
    k = 1
    while len(L)!=0:
        ret.extend(L)

        L = apriori_next(D,L,k,minsup)
        k += 1

    return ret

def freqSet(retItems,item):
    for i in retItems:
        if i[0]==item:
            return i[1]
    return 0

def getSupport(D,retItems,c):
    return (float)(freqSet(retItems,c))/len(D)

def subsets(arr):
    return chain(*[combinations(arr,i+1) for i in range(len(arr))])

def getRules(D,minsup,minconf):
    retItems = apriori(D,minsup*len(D))
    retRules = []
    for i in retItems:
        _subsets = map(set, [x for x in subsets(i[0])])
        for elem in _subsets:
            remain = i[0].difference(elem)
            if len(remain)>0:
                try:
                    conf = getSupport(D,retItems,i[0])/getSupport(D,retItems,elem)
                except:
                    conf = 0

                if conf>=minconf:
                    retRules.append((elem,remain,conf,getSupport(D,retItems,i[0])))
    retRules.sort(key=lambda x:x[2],reverse=True)
    return retRules


if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option('-f','--file',
                        dest='input',
                        help='file path of input file',
                        default=None)
    optparser.add_option('-s','--minSupport',
                        dest='minsup',
                        help='minimum support value',
                        default=0.1,
                        type='float')
    optparser.add_option('-c','--minConfidence',
                        dest='minconf',
                        help='minimum confidence value',
                        default='0.5',
                        type='float')
    optparser.add_option('-k','--topK',
                        dest='topk',
                        help='print top K rules',
                        default=None,
                        type='int')

    (options, args) = optparser.parse_args()

    D = []
    if options.input is None:
        print('No dataset filename specified.')
        sys.exit()
    else:
        with open(options.input, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                D.append(set(row))

    minsup = options.minsup
    minconf = options.minconf
    k = options.topk

    rules = getRules(D,minsup,minconf)
    print('LHS => RHS : confidence support')
    if k is None:
        for r in rules:
            print(str(r[0])+' => '+str(r[1])+' : '+str(r[2])+' '+str(r[3]))
    else:
        for i,r in enumerate(rules):
            if i>=k:
                break
            print(str(r[0])+' => '+str(r[1])+' : '+str(r[2])+' '+str(r[3]))
