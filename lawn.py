
"""
 grass.py - Grass interpreter
 http://www.blue.sky.or.jp/grass/

 Copyright (C) 2008 NISHIO Hirokazu. All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS''
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 History:

 2008-06-06
   - Tlanslated to python by NISHIO
 2007-10-02
   - Follow the latest changes of the definition of Grass.
   - by UENO Katsuhiro
 2007-09-20
   - First version by UENO Katsuhiro.


TESTS
>>> run("wWWwwww")
w

>>> run('''wwWWwv \
    wwwwWWWwwWwwWWWWWWwwwwWwwv \
    wWWwwwWwwwwWwwwwwwWwwwwwwwww''')
ww

>>> run("wWWWwwwwWWWw") # x
x

"""

"""
Lawn Interpreter

by Thomas Quanci

Retrofitted from NISHIO Hirokazu's Grass interpreter.
"""

from copy import deepcopy
import sys
import re

RELEASE = 0
ONLY_RETURN = 40
DEBUG = 50
DEBUG2 = 60
LOGLEVEL = RELEASE
NUMERICAL_OUTPUT = False
def log(level, *msg):
    if level <= LOGLEVEL:
        print("\t".join(map(str, msg)))

def Struct(*keys):
    class _Struct(object):
        def __init__(self, *values):
            self.__dict__.update(zip(keys, values))
    return _Struct

Machine = Struct("code", "env", "dump")

    
class Value(object):
    def __repr__(self):
        return self.__class__.__name__

class Insn(object):
    pass

class App(Insn):
    def __init__(self, m, n):
        self.m = m
        self.n = n

    def eval(self, m):
        f, v = m.env[-self.m], m.env[-self.n]
        log(DEBUG2, "Application:\n\tfunc:%s\n\targ:%s\n" %
            (f, v))
        f.app(m, v)

    def __repr__(self):
        return "App(%(m)d, %(n)d)" % self.__dict__


class Abs(Insn):
    def __init__(self, body):
        self.body = body

    def eval(self, m):
        m.env.append(Fn(self.body, deepcopy(m.env)))

    def __repr__(self):
        return "Abs(%s)" % self.body

class Fn(Value):
    count = 0
    name = ""
    def __init__(self, code, env):
        self.code, self.env = code, env
        Fn.count += 1
        self.count = Fn.count
        log(DEBUG2, "Fn%d:\n\tcode:%s\n\tenv:%s\n" %
            (self.count, self.code, self.env))
        
    def app(self, m, arg):
        m.dump.append((m.code, m.env))
        m.code, m.env = deepcopy(self.code), deepcopy(self.env)
        m.env.append(arg)

    def __repr__(self):
        if self.name:
            return self.name
        return "Fn%d" % self.count

ChurchTrue  = Fn([Abs([App(3,2)])], [Fn([],[])])
ChurchTrue.name = "CTrue"
ChurchFalse = Fn([Abs([])], [])
ChurchFalse.name = "CFalse"

class CharFn(Value):
    def __init__(self, char_code):
        self.char_code = char_code

    def app(self, m, arg):
        if self.char_code == arg.char_code:
            ret = ChurchTrue
        else:
            ret = ChurchFalse
        m.env.append(ret)

    def __repr__(self):
        return "Char(%s)" % self.char_code

class Succ(Value):
    def app(self, m, arg):
        m.env.append(CharFn((arg.char_code + 1) & 255))

class Out(Value):
    def app(self, m, arg):
        if NUMERICAL_OUTPUT:
            sys.stdout.write("%d(%c)" % (arg.char_code, arg.char_code))
        else:
            sys.stdout.write(chr(arg.char_code))
        m.env.append(arg)


class In(Value):
    def app(self, m, arg):
        ch = sys.stdin.read(1)
        if ch == "":
            ret = arg
        else:
            ret = CharFn(ord(ch))
        m.env.append(ret)

def eval(m):
    while True:
        log(DEBUG, "code:", m.code)
        log(DEBUG, "env:", m.env)
        log(DEBUG, "dump:", m.dump)
        log(DEBUG)
        
        if not m.code:
            if not m.dump: break
            ret = m.env[-1]
            m.code, m.env = m.dump.pop()
            m.env.append(ret)
            log(ONLY_RETURN, m.env)
        else:
            insn = m.code.pop(0)
            insn.eval(m)

    return m.env[0]

InitialEnv = [In(), CharFn(0), Succ(), Out()]
InitialDump = [[[], []], [[App(1, 1)], []]]

def start(code):
    return eval(Machine(code, deepcopy(InitialEnv), deepcopy(InitialDump)))

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
    """
    #Grass Parser
    src = re.subn("[^wｗ]*", "", src, 1)[0] #remove anything at start that isn't 'w'
    src = re.sub("[^wｗWＷvｖ]", "", src) #remove any illegal charcters
    for s in re.split("[vｖ]+", src): #split code into apps and defs at 'v'
        if not s: continue
        a = re.findall(r"[wｗ]+|[WＷ]+", s) #break up section into chains of 'w's and 'W's
        a = list(map(len, a)) #convert chains into numbers
        arity = 0 #function arity, 0 if app
        if s[0] in "wｗ": #if section is a def...
            arity = a.pop(0) #first number is arity, and remove it, to leave only apps
        if len(a) % 2 != 0: raise RuntimeError("parse error at app") #check if code is valid
        body = [] #empty list of applications

        for i in range(0, len(a) - 1, 2): 
            body.append(App(a[i], a[i+1])) #apply function at index a[i] to thing at index a[i+1] and put it at the end of body

        for i in range(arity):
            body = [Abs(body)] #for every argument of the fuction definition, abstract body

        code += body
    """
    #Lawn Parser
    names = [[False, "in", 4], [False, "0", 3], [False, "suc", 2], [False, "out", 1]] #store labels [[local, name, index],[...],...]
               #local is a bool
               #name is a string
               #index is an int
    code = []
    
    src = re.sub(r"#[^#]*#", "", src) # remove comments
    src = re.sub(r":", " : ", src) # split any ':' from their suroundings
    src = re.sub(r"]", " ] ", src) #split any ']' from their surroundings
    src = re.split(r"\s+", src) # split into chunks at spaces
    while(not src[0].isnumeric()): #get rid of stuff before first function
        src.pop(0)

    m=-1
    a=[]
    define=False
    for i in range(len(src)):  #split function into defs and apps
        if not src[i]: continue
        elif src[i].isnumeric() and src[i]!= '0':
            if define == False:
                define = True
                a.append([src[i]])
                m = m+1
            else: raise RuntimeError("parse error at app: nested defs")
        elif src[i] == ']':
            if define == True:
                define = False
                if not src[i+1].isnumeric():
                    a.append([])
                    m = m+1
            else: raise RuntimeError("parse error at app: unexpected ']'")
        else:
            a[m].append(src[i])
    a = [x for x in a if x]
    if define == True: raise RuntimeError("parse error at app: missing ']'")

    for s in a: # convert defs and apps into numeric indices and pass them to the stack
        local = False
        arity = 0
        count = 0
        if s[0].isnumeric() and s[0] != "0":
            local = True
            arity = int(s[0])
            s.pop(0)
            for i in range(arity):
                updateNamelist(names)
                addName(names, True, "".join((".",str(i+1))))
        if (len(s) % 2) != 0: raise RuntimeError("parse error at app: wrong number of terms")
        for n in range(len(s)):
            if not s[n]: continue
            if s[n] == ":":
                if n%2 != 0: raise RuntimeError("parse error at app: unexpected ':'")
                if (not re.sub(r"\.0*[1-9]+[0-9]*","",s[n+1])) or (not re.sub("'0*[1-9]+[0-9]*|'","",s[n+1])):
                    raise RuntimeError("parse error at app: illegal name")
                else: addName(names, local, s[n+1])
                s[n] = ""
                s[n+1] = ""
            elif s[n][0] == "'":
                s[n] = s[n][1:]
                if s[n].isnumeric(): 
                    if int(s[n]) != 0:
                        s[n] = int(s[n])
                    else:
                        raise RuntimeError("parse error at app: ''' has no index")
                elif not s[n]: s[n] = 1
                else: raise RuntimeError("parse error at app: ''' has no index")
            else:
                s[n] = lookupName(names, s[n])
            if n % 2 != 0: 
                count = count + 1
                updateNamelist(names)
        s = [x for x in s if x]
        clearLocal(names, arity + (count-1)*local)
        
        
        body = [] #empty list of applications

        for i in range(0, len(s) - 1, 2): 
            body.append(App(s[i], s[i+1])) #apply function at index a[i] to thing at index a[i+1] and put it at the end of body

        for i in range(arity):
            body = [Abs(body)] #for every argument of the fuction definition, abstract body

        code += body

    return code

def run(src):
    start(parse(src))


## coding utilities
env = ["In", "w", "Succ", "Out"]

def ws(name, env=env):
    return "w" * find_last(env, name)

def Ws(name, env=env):
    return "W" * find_last(env, name)

def find_last(xs, x):
    for i in range(len(xs)):
        if xs[-1-i] == x:
            return i + 1

def make_func(name, body):
    """
    build function body
    body format:
    [("resultname", "funcname", "argname"), ...]
    for example
    [("arg+1", "Succ", "arg1"), ("arg+2", "Succ", "arg1")]

    >>> print(make_func("+2", [\
            ("tmp", "Succ", "arg1"),\
            ("result", "Succ", "tmp"),\
            ]))
    wWWWwWWWWwv
    <BLANKLINE>
    >>> print(make_func("+4", [\
            ("tmp", "+2", "arg1"),\
            ("result", "+2", "tmp"),\
            ]))
    wWWwWWWwv
    <BLANKLINE>
    """
    myenv = deepcopy(env)
    myenv.append("arg1")
    result = "w"
    for (fn, f, a) in body:
        result += Ws(f, myenv)
        result += ws(a, myenv)
        myenv.append(fn)
    env.append(name)
    return result + "v\n"

def build_helloworld():
    code = (
        make_func("+2", [
            ("tmp", "Succ", "arg1"),
            ("result", "Succ", "tmp"),
            ])+
        make_func("+4", [
            ("tmp", "+2", "arg1"),
            ("result", "+2", "tmp"),
            ])+
        make_func("+8", [
            ("tmp", "+4", "arg1"),
            ("result", "+4", "tmp"),
            ])+
        make_func("+16", [
            ("tmp", "+8", "arg1"),
            ("result", "+8", "tmp"),
            ])+
        make_func("+32", [
            ("tmp", "+16", "arg1"),
            ("result", "+16", "tmp"),
            ])+
        make_func("+64", [
            ("tmp", "+32", "arg1"),
            ("result", "+32", "tmp"),
            ])+
        make_func("+128", [
            ("tmp", "+64", "arg1"),
            ("result", "+64", "tmp"),
            ])+
        make_func("print", [
            ("128w", "+128", "w"),
            ("...+32w", "+32", "128w"),
            ("...+64w", "+64", "...+32w"),
            ("...+16w", "+16", "...+64w"),
            ("...+1w", "Succ", "...+16w"),
            ("l", "+4", "...+1w"),
            ("tmp", "+2", "...+1w"),
            ("r", "+8", "tmp"),
            
            ("o", "+8", "...+16w"),

            ("tmp", "+8", "...+64w"),
            ("tmp", "+4", "tmp"),
            ("e", "+2", "tmp"),
            ("d", "Succ", "tmp"),

            ("tmp", "Succ", "...+32w"),
            (" ", "+8", "tmp"),
            ("tmp", "+16", "tmp"),
            (",", "+4", "tmp"),
            ("tmp", "+2", "...+32w"),
            ("!", "+8", "tmp"),

            ("tmp", "Succ", "128w"),
            ("tmp", "+64", "tmp"),
            ("H", "+16", "tmp"),
            ("tmp", "Out", "H"),
            ("tmp", "Out", "e"),
            ("tmp", "Out", "l"),
            ("tmp", "Out", "l"),
            ("tmp", "Out", "o"),
            ("tmp", "Out", ","),
            ("tmp", "Out", " "),
            ("tmp", "Out", "w"),
            ("tmp", "Out", "o"),
            ("tmp", "Out", "r"),
            ("tmp", "Out", "l"),
            ("tmp", "Out", "d"),
            ("tmp", "Out", "!"),
            ])
    )
    import textwrap
    for line in textwrap.wrap(code):
        print(line)
    run(code)

def _test():
    import importlib
    import doctest
    importlib.reload(doctest)
    doctest.testmod()
    print("ok.")

def run_stdin():
    with open(sys.argv[1], 'r') as f:
        src = f.read()
    run(src)
    
if __name__ == "__main__":
    #_test()
    run_stdin()    
    #build_helloworld()
