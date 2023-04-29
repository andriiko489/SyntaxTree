import json

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from nltk import *
import random
import itertools


def randpop(a):
    geted = random.choice(a)
    a.remove(geted)
    return geted


def firstpop(a):
    geted = a[0]
    a.remove(geted)
    return geted


def findNPs(tree):
    queue = [tree]
    needed = []
    while len(queue) != 0:  #
        labels = []
        for i in queue[0]:
            if type(i) != str:
                labels.append(i.label())
        # print(labels)
        if (queue[0].label() == "NP") and (labels.count("NP") >= 2) and (labels.count("CC") + labels.count(",") >= 1):
            needed.append(queue[0])
        if queue[0]:
            for i in range(len(queue[0])):
                if type(queue[0][i]) != str:
                    queue.append(queue[0][i])
        del queue[0]
    return needed


def shuf(a, np_nums, cc_nums):
    NPs = [i for i in a if i.label() == "NP"]
    CCs = [i for i in a if i.label() in ["CC", ","]]
    first = NPs[firstpop(np_nums)]
    last = NPs[firstpop(np_nums)]
    b = Tree('NP', [first])
    # print(NPs, np_nums, CCs, cc_nums)
    while 1:
        if cc_nums:
            b.append(CCs[firstpop(cc_nums)])
        if np_nums:
            b.append(NPs[firstpop(np_nums)])
        else:
            break
    b.append(last)
    # print(b)
    return ParentedTree.convert(b)


def perm(a):
    nps = 0
    ccs = 0
    result = []
    b = a.root().copy()
    bi = a.treeposition()
    # print(123)
    # print(b[bi])
    for i in a:
        if i.label() == "NP":
            nps += 1
        if i.label() in ["CC", ","]:
            ccs += 1
    for i in itertools.permutations(range(nps)):
        for j in itertools.permutations(range(ccs)):
            b[bi] = shuf(a, list(i), list(j))
            result.append(b.copy())
    return result


def remove_spaces_endl(a):
    a = ' '.join(a.split("\n"))
    l = a.split(" ")
    while '' in l:
        l.remove('')
    a = ' '.join(l)
    return a


def paraphrase(request):
    tree = ParentedTree.fromstring(request.GET["tree"])
    limit = 20
    if "limit" in request.GET.keys():
        try:
            limit = int(request.GET["limit"])
        except:
            HttpResponse("Wrong type of limit")
    needed = findNPs(tree)
    result = {"paraphrases": []}
    num_of_perms = 0
    for i in needed:
        for j in perm(i):
            if num_of_perms >= limit:
                break
            result["paraphrases"].append({"tree": remove_spaces_endl(str(j))})
            num_of_perms += 1
        else:
            continue
        break
    s = json.dumps(result, indent=4)
    return HttpResponse("<pre>{}</pre>".format(s))
