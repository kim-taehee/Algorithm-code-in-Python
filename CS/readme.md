# CS algorithm codes
CS algorithms


## [최단거리(makespan)](https://github.com/kim-taehee/Advanced--code-in-Python/blob/master/CS/makespan.ipynb)  
prim's의 최단거리 




codility2
# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")

def solution(A):
    # write your code in Python 3.6
    char=[str(s) for s in A]
    x=set(char)
    dup=[]
    for c in x:
        if(char.count(c)<2):
            dup.append(c)
    result=int(dup[0])
    return result
