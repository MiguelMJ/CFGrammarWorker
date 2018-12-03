verbose = False

class Rule:
    def __init__(self, A, C):
        self.A = A
        self.C = C.split()
    def __init__(self, str):
        list = str.split("->")
        self.A = list[0].replace(" ","")
        self.C = list[1].split()
    def __str__(self):
        
        return str(self.A) + " -> " + " ".join(self.C)
    def __repr__(self):
        
        return repr(self.A) + " -> " + " ".join(self.C)
    def __eq__(self,other):
        
        return self.A == other.A and self.C == other.C
    def __lt__(self,other):
        return self.A < other.A or (self.A == other.A and self.C < other.C)
    def __hash__(self):
        return hash((str(self.A)+str(self.C)))
    
class Grammar:
    def __init__(self):
        self.ruleset = dict()
        self.rulelist = []
        self.N = set()
        self.T = set()
        self.Axiom = None
        self.NUT = set()
        self.waitingFirst = set()
        self.waitingFollow = set()
        self.EPSILON = "_"
        self.firstCache = {}
        self.followCache = {}
        self.firstSymbolsCache = {}
    def loadFromFile(self,filename):
        self.__init__()
        index = 0;
        file = open(filename)
        text = file.read()
        rules = text.split("\n")
        for r in rules:
            if r and not r in self.ruleset:
                self.addRule(r)
                self.rulelist.append(r)
    def addRule(self, str):
        newrule = Rule(str)
        if not self.ruleset:
            self.Axiom = newrule.A
        if not newrule.A in self.ruleset:
            self.ruleset[newrule.A] = set()
            self.N.add(newrule.A);
        self.T.update()
        self.ruleset[newrule.A].add(newrule)
        self.NUT.update(newrule.A);
        self.NUT.update(newrule.C);
        self.T = self.NUT - self.N;
    def ruleByNumber(self, n):
        return rulelist[n]
    def first(self, N):
        if N in self.firstCache:
            ret = self.firstCache[N]
        else:
            self.waitingFirst = set()
            ret = set();
            for c in N.split(" "):
                lastSymFirst = self.first_aux(c)
                ret.update(lastSymFirst)
                if not self.EPSILON in lastSymFirst:
                    if self.EPSILON in ret:
                        ret.remove(self.EPSILON)
                    break
            self.firstCache[N] = ret
        return ret;
    def first_aux(self, N):
        if not N or N == self.EPSILON:
            return {self.EPSILON}
        if N in self.T:
            return {N}
        if not N in self.N:
            print("Symbol unknown: "+N)
            return {}
        if verbose:
            print("-"*len(self.waitingFirst),end='')
            print("called CAB(" + N + ")")
        ret = set()
        for r in self.ruleset[N]: # para cada regla
            if not r in self.waitingFirst: # si la regla no esta en espera, para evitar bucles infinitos
                retrule = set()
                if verbose:
                    print("-"*len(self.waitingFirst),end='')
                    print(r)
                conc = r.C
                self.waitingFirst.add(r);
                for s in conc: # para cada simbolo del consecuente
                    retsym = self.first_aux(s)
                    retrule.update(retsym)
                    if verbose:
                        print("-"*len(self.waitingFirst),end='')
                        print("added " + str(retsym) + " to " + str(retrule))
                    if not self.EPSILON in retsym:
                        if self.EPSILON in retrule:
                            retrule.remove(self.EPSILON)
                        if verbose:
                            print("-"*len(self.waitingFirst),end='')
                            print(self.EPSILON + " not in " + str(retsym) + ": removed epsilon from this rule and no further searching to do in it.")
                        break
                ret.update(retrule)
                self.waitingFirst.remove(r);
        if verbose:
            cab = "CAB("+N+") = "
            print("-"*len(self.waitingFirst),end='')
            print(cab+str(ret))
        return ret
    def follow(self,N):
        if N in self.followCache:
            ret = self.followCache[N]
        else:
            self.waitingFollow = set()
            ret = self.follow_aux(N)
        return ret
    def follow_aux(self,N):
        ret = set()
        if not N in self.waitingFollow:
            self.waitingFollow.add(N)
            if verbose:
                print("-"*len(self.waitingFollow),end='')
                print("Called SIG("+N+")")
            for k in self.ruleset:
                for r in self.ruleset[k]:
                    if N in r.C:
                        if verbose:
                            print("-"*len(self.waitingFollow),end='')
                            print(r)
                        conc = "".join(r.C)
                        i = conc.find(N)
                        while i != -1:
                            conc = conc[i+1:]
                            if verbos:
                                print("-"*len(self.waitingFollow),end='')
                                print(conc)
                            if conc:
                                ret.update(self.first(conc))
                            else:
                                ret.update(self.follow_aux(k))
                            if self.EPSILON in ret:
                                ret.remove(self.EPSILON)
                                ret.update(self.follow_aux(k))
                            i = conc.find(N)
        if verbose:
            print("-"*len(self.waitingFollow),end='')
            print("SIG("+N+") = ",end='')
            print(ret)
        return ret
    def firstSymbols(rule):
        ret = set()
        conc = rule.C
        ant = rule.A
        ret = self.first(conc)
        if self.EPSILON in ret:
            ret.remove(self.EPSILON)
            ret.update(self.follow(ant))
        return ret
    def dumpNonTerminals(self):
        return str(sorted(self.N))
    def dumpTerminals(self):
        return str(sorted(self.T))
    def dumpSymbols(self):
        return str(sorted(set.union(self.N,self.T)))
    def dumpRules(self):
        ret = ""
        for index in range(len(self.rulelist)):
            ret += "{:<4}".format("R"+str(index)+".") + str(self.rulelist[index]) + "\n"
        return ret
    def dumpAxiom(self):
        return str(self.Axiom)
    def __str__(self):
        ret = "\nNON TERMINAL SYMBOLS\n"
        ret +=   "--------------------\n"
        ret += self.dumpNonTerminals()
        ret += "\n\nTERMINAL SYMBOLS\n"
        ret +=   "----------------\n"
        ret += self.dumpTerminals()
        ret += "\n\nAXIOM\n"
        ret +=   "-----\n"
        ret += self.dumpAxiom()
        ret += "\n\nRULES\n"
        ret +=   "-----\n"
        ret += self.dumpRules()
        return ret
    def __repr__(self):
        ret = ""
        for key in sorted(self.ruleset.keys()):
            for rule in sorted(self.ruleset[key]):
                ret += repr(rule) + '\n'
        return ret
    
cmd = ""
g = Grammar()
while not cmd in {"exit","quit","end"}:
    cmd = input(">")
    args = cmd.split(" ")
    if args[0] == "cab":
        for i in args[1:]:
            print(g.first(i))
    elif args[0] == "sig":
        for i in args[1:]:
            print(g.follow(i))
    elif args[0] == "load":
        g.loadFromFile(args[1])
    elif args[0] == "dump":
        print(g)
    elif args[0] == "verbose":
        verbose = not verbose
        print("verbose = "+str(verbose));
    
    
    
    
    
    
    
    
    
