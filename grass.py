#Grass Interpreter
#by moss quanci

import sys
import re

def lout(a): #primitive OUT
    if type(a) is str:
        sys.stdout.write(a)
        return a
    else:
        raise RuntimeError("execution halted: primitive out was passed a non-character argument")

def lin(a): #primitive IN
    c = sys.stdin.read(1)
    if c == "":
        return a
    else:
        return c

def lsuc(a): #primitive SUC
    if type(a) is str:
        return chr((ord(a)+1) & 255)
    else:
        raise RuntimeError("execution halted: primitive suc was passed a non-character argument")

def lchar(a, c): #(primitive) character behavior
    if (type(a) is str) and (a == c):
        return [-1, []] #Church true
    else:
        return [-2, []] #Church false

stack = [lin, "w", lsuc, lout]

class Func: #class of function "closures"
    def __init__(self, pos, ari, lis):
        self.pos = pos #index of item on main stack before closure
        self.ari = ari #arity
        self.lis = lis #list of applications

def lapply(app, pos, fstack=[]): #app is application tuple, pos is last usable index of stack, fstack is the current function stack
    global stack
    apos = len(fstack)-app[0] #find the index for a and b in stack and fstack
    bpos = len(fstack)-app[1]
    if apos >=0: #find value of a and b
        a = fstack[apos]
    else:
        a = stack[apos+pos+1]
    if bpos >=0:
        b = fstack[bpos]
    else:
        b = stack[bpos+pos+1]
    if callable(a): #a is primitive
        return a(b)
    if type(a) is str: # a is a character
        return lchar(b, a)
    if type(a) is Func: #a is a function closure
        if a.ari==1:
            return runf(a.pos+1, [b])
        else:
            return [a.pos+1, [b]]
    if type(a) is list: #a is a function closure missing arguments
        if a[0]<0:
            left = 2
        else:
            left = stack[a[0]].ari
        if (left-len(a[1])) == 1:
            return runf(a[0], a[1]+[b])
        else:
            return [a[0], a[1]+[b]]

def runf(pos, fstack): #execute a function at stack index pos with complete args in list fstack
    global stack
    global depth
    if pos == -1: #Church true
        return fstack[0]
    if pos == -2: #Church false
        return fstack[1]
    func = stack[pos]
    for app in func.lis:
        fstack.append(lapply(app, func.pos, fstack))
    return fstack[-1]

def run(code):
    global stack
    stack = [lin, "w", lsuc, lout]
    cur = 3 #last available index
    for x in code:
        if type(x) is Func:
            x.pos = cur
            stack.append(x)
            cur += 1
        else:
            stack.append(lapply(x, cur))
            cur += 1
    return lapply((1,1),cur)

def parse(src):
    code = []
    
    src = re.subn("[^wｗ]*", "", src, 1)[0] #remove anything at start that isn't 'w'
    src = re.sub("[^wｗWＷvｖ]", "", src) #remove any illegal charcters
    for s in re.split("[vｖ]+", src): #split code into apps and defs at 'v'
        if not s: continue
        a = re.findall(r"[wｗ]+|[WＷ]+", s) #break up section into chains of 'w's and 'W's
        a = list(map(len, a)) #convert chains into numbers
        arity = 0 #function arity, 0 if app
        if s[0] in "wｗ": #if section is a def...
            arity = a.pop(0) #first number is arity, and remove it, to leave only apps
        if len(a) % 2 != 0: raise RuntimeError("parse error: wrong number of terms") #check if code is valid
        
        apps = [] #empty list of applications within a function

        for i in range(0, len(a) - 1, 2): 
            if arity == 0:
                code.append((a[i], a[i+1]))
            else:
                apps.append((a[i], a[i+1]))
        if arity:
            code.append(Func(0,arity,apps))
    return code

if __name__ == "__main__":
    with open(sys.argv[1], 'r',encoding="utf-8") as f:
        src = f.read()
    run(parse(src))