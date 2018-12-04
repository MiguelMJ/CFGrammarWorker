#!/usr/bin/python3
import os

verbose = False

class Rule:
    def __init__(self, A, C):
        self.A = A
        self.C = C.split()
    def __init__(self, str):
        list = str.split("->")
        if len(list) < 2:
            print("error in rule "+list.__str__())
        elif verbose:
            print("correctly read rule: "+list.__str__());
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
        self.ll1table = dict()
        self.ll1condition = None
    def loadFromFile(self,filename):
        self.__init__()
        index = 0;
        file = open(filename)
        text = file.read()
        rules = text.split("\n")
        for r in rules:
            if r:
                self.addRule(r)
                
    def addRule(self, str):
        newrule = Rule(str)
        if not self.ruleset:
            self.Axiom = newrule.A
        if not newrule.A in self.ruleset:
            self.ruleset[newrule.A] = set()
            self.N.add(newrule.A);
        if not newrule in self.ruleset[newrule.A]:
            self.ruleset[newrule.A].add(newrule)
            self.rulelist.append(newrule)
        self.NUT.update(newrule.A)
        self.NUT.update(newrule.C)
        self.T = self.NUT - self.N;
        if self.EPSILON in self.T:
            self.T.remove(self.EPSILON)
        
    def ruleByNumber(self, n):
        return self.rulelist[n]
    
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
                            if verbose:
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
    
    def firstSymbols(self,rule):
        ret = set()
        if rule.isdigit():
            rule = self.ruleByNumber(int(rule))
        if rule in self.firstSymbolsCache:
            ret = self.firstSymbolsCache[rule]
        else:
            conc = rule.C
            ant = rule.A
            ret = self.first(" ".join(conc))
            if self.EPSILON in ret:
                ret.remove(self.EPSILON)
                ret.update(self.follow(ant))
            self.firstSymbolsCache[rule] = ret
        return ret
    def LL1(self, N, T):
        ret = list()
        if (N,T) in self.ll1table:
            ret = self.ll1table[N,T]
        else:
            for ind,rule in enumerate(self.rulelist):
                if rule.A == N and T in self.firstSymbols(str(ind)):
                    ret.append(" ".join(rule.C))
            self.ll1table[N,T] = ret
        return ret
    def LL1condition(self):
        if self.ll1condition == None:
            ret = True
            for n in self.N:
                for t in self.T:
                    ret = len(self.LL1(n,t)) < 2
                    if not ret:
                        break
                if not ret:
                    break
        else:
            ret = self.ll1condition
        return ret
    def LL1analysis(self,cad):
        if self.LL1condition():
            stack = list(self.Axiom)
            cad = list(cad)
            error = False
            counter = 1
            while not error and stack and cad:
                print(counter,"---")
                print("left:",cad)
                print("stack:",stack)
                counter += 1
                x = stack[0]
                a = cad[0]
                if x in self.N:
                    alpha = self.LL1(x,a)[::-1]
                    if len(alpha) == 0:
                        error = True
                        print("No match in LL(1) table")
                    else:
                        print(x,"->",alpha)
                        stack = alpha[0].split() + stack[1:]
                elif x in self.T:
                    if x == a:
                        print("Accepted symbol:",a);
                        stack = stack[1:]
                        cad = cad[1:]
                    else:
                        error = True
                        print("Symbol",x,"not expected. Instead",self.first(stack[0]))
                else:
                    error = True
                    print("Symbol",x,"not in alphabet",self.NUT)
            print("---")
            if error or stack or cad:
                print("String not recognized")
                print("stack:",stack)
                print("string:",cad)
            else:
                print("Strings belongs to the language.")
        else:
            print("LL(1) condition not satisfied")
            return None
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
    def dumpFirstSymbols(self):
        ret = ""
        for index in range(len(self.rulelist)):
            ret += "{:<5}".format("SD(") + str(self.rulelist[index]) + ") = " + str(self.firstSymbols(str(index))) +"\n"
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
    
os.system('figlet CFGW')
print('Context Free Grammar Worker')
print('https://github.com/MiguelMJ/CFGrammarWorker/')
print('............................................')
cmd = ""
g = Grammar()
prompt = "NoGrammar"
while not cmd in {"exit","quit","end"}:
    cmd = input("\033[38;2;0;150;0m"+prompt+" >> \033[0m")
    args = cmd.strip().split(" ")
    cmd = args[0].lower()
    if cmd in {"cab","first"}:
        for i in args[1:]:
            print(g.first(i))
    elif cmd in {"sig","follow"}:
        for i in args[1:]:
            print(g.follow(i))
    elif cmd in {"sd","fs","firstsymbols"}:
        for i in args[1:]:
            if i and i.isdigit():
                print(g.ruleByNumber(int(i)))
                print(g.firstSymbols(i))
    elif cmd in {"ll1table"}:
        for n in g.N:
            for t in g.T:
                print("LL1("+n+","+t+")","=",g.LL1(n,t))
    elif cmd in {"ll1"}:
        if len(args) == 1:
            print(g.LL1condition())
        else:
            g.LL1analysis(args[1:])
        
    elif cmd in {"load"}:
        g.loadFromFile(args[1])
        prompt = args[1]
    elif cmd in {"dump", "print"}:
        for what in args[1:]:
            if what.lower() in {"rules"}:
                print(g.dumpRules())
            if what.lower() in {"sd","fs","firstsymbols"}:
                print(g.dumpFirstSymbols())
            elif what.lower() in {"nonterminals", "N"}:
                print(g.dumpNonTerminals())
            elif what.lower() in {"terminals", "T"}:
                print(g.dumpTerminals())
            elif what.lower() in {"axiom"}:
                print(g.dumpAxiom())
        if len(args) == 1:
            print(g)
    elif cmd == "verbose":
        verbose = not verbose
        print("verbose = "+str(verbose));
    elif cmd.isdigit():
        if int(cmd) < len(g.rulelist):
            print("{:<4}".format("R"+cmd+"."), end='')
            print(g.ruleByNumber(int(cmd)))
        else:
            print("Rules indexed between 0 and "+str(len(g.rulelist)-1))
    elif not cmd in {"exit","quit","end"}:
        print("Unknown command")
    
    
    
    
    
    
    
    
    
