#Lawn to Grass Converter
#by moss quanci

import sys
import re

class Lfunc: #class of function "closures"
    def __init__(self, pos, ari, lis):
        self.pos = pos #index of item on main stack before closure
        self.ari = ari #arity
        self.lis = lis #list of applications

def updateNamelist(namelist):
    for n in range(len(namelist)):
        namelist[n][2] = namelist[n][2] + 1
        
def addName(namelist, local, name):
    for n in range(len(namelist)):
        if namelist[n][1] == name: raise RuntimeError("parse error at app: namespace collision")
    namelist.append([local, name, 1])
    
def lookupName(namelist, name):
    i = [x[1] for x in namelist].index(name)
    return namelist[i][2]
    
def clearLocal(namelist, undo):
    i=0
    while i < len(namelist):
        namelist[i][2] = namelist[i][2] - undo
        if namelist[i][0]: namelist.pop(i)
        else: i=i+1

def parse(src):
    names = [[False, "in", 4], [False, "w", 3], [False, "suc", 2], [False, "out", 1]] #store labels [[local, name, index],[...],...]
               #local is a bool
               #name is a string
               #index is an int
    code = []
    
    src = re.sub(r"#[^#]*#", "", src) # remove comments
    src = re.sub(r":", " : ", src) # split any ':' from their suroundings
    src = re.sub(r"]", " ] ", src) #split any ']' from their surroundings
    src = re.split(r"\s+", src) # split into chunks at whitespace
    src = [x for x in src if x]
    while (not src[0].isnumeric()) or (not src[0].replace('0', '')): #get rid of stuff before first function def
        src.pop(0)

    m=-1
    a=[]
    define=False
    for i in range(len(src)):  #split function into defs and apps
        if not src[i]: continue
        if src[i].isnumeric() and src[i]!= '0': #if function def
            if define == False:
                define = True
                a.append([src[i]]) #append a list containing arity string as first element to a
                m = m+1
            else: raise RuntimeError("parse error: nested functions")
        elif src[i] == ']': #if end of function def
            if define == True:
                define = False
                if i != len(src)-1:
                    if (not src[i+1].isnumeric()) or (src[i+1] == '0'): #if the next part of src is not a func def
                        a.append([]) #append a blank list
                        m = m+1
            else: raise RuntimeError("parse error: unexpected ']'")
        else:
            a[m].append(src[i])
    a = [x for x in a if x]
    if define == True: raise RuntimeError("parse error: missing ']'")

    for s in a: # convert defs and apps into numeric indices and pass them to the stack
        local = False
        arity = 0
        count = 0
        if s[0].isnumeric() and s[0] != "0": #if list s in a is a function def
            local = True
            arity = int(s[0])
            s.pop(0)
            for i in range(arity): #add names for args to namelist
                updateNamelist(names)
                addName(names, True, "".join((".",str(i+1))))
        if (len(s) % 2) != 0: raise RuntimeError("parse error: wrong number of terms")
        for n in range(len(s)):
            if not s[n]: continue
            if s[n] == ":": #declare a new name
                if n%2 != 0: raise RuntimeError("parse error: unexpected ':'")
                if (not re.sub(r"\.0*[1-9]+[0-9]*","",s[n+1])) or (not re.sub("'0*[1-9]+[0-9]*|'","",s[n+1])) or (s[n+1] == ":"): #conditions for a name
                    raise RuntimeError("parse error: illegal name")
                else: addName(names, local, s[n+1])
                s[n] = ""
                s[n+1] = ""
            elif s[n][0] == "'": #if relative index
                s[n] = s[n][1:] #remove '
                if s[n].isnumeric(): 
                    if int(s[n]) != 0:
                        s[n] = int(s[n])
                    else:
                        raise RuntimeError("parse error: ''' has no index")
                elif not s[n]: s[n] = 1
                else: raise RuntimeError("parse error: ''' has no index")
            else: #treat s as named entity
                s[n] = lookupName(names, s[n])
            if n % 2 != 0: #if we have completed a set of terms i.e. one item on the stack 
                count = count + 1
                updateNamelist(names)
        s = [x for x in s if x]
        clearLocal(names, arity + (count-1)*local)
        
        
        apps = [] #empty list of applications within a function

        for i in range(0, len(s) - 1, 2): 
            if arity == 0:
                code.append((s[i], s[i+1]))
            else:
                apps.append((s[i], s[i+1]))
        if arity:
            code.append(Lfunc(0,arity,apps))
        
    grass=""
    for x in code:
        if type(x) is Lfunc:
            if grass != "":    
                if grass[-1] !='v': grass += "v"
            grass += "w"*x.ari
            for y in x.lis:
                grass += "W"*y[0]
                grass += "w"*y[1]
            grass += "v"
        else:
            grass += "W"*x[0]
            grass += "w"*x[1]
    if grass[0] == 'v':
        grass = grass[1:]
    if grass[-1] == 'v':
        grass = grass[:-1]
    return grass

if __name__ == "__main__":
    with open(sys.argv[1], 'r', encoding="utf-8") as f:
        src = f.read()
    with open(sys.argv[2], 'w', encoding="utf-8") as f:
        f.write(parse(src))