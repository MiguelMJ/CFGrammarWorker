#!/usr/bin/python3
import os

verbose = False

class LR0Item:
    def __init__(self,A,alpha=None,beta=None):
        if alpha!=None and beta!=None:
            self.A = A
            self.Alpha = alpha
            self.Beta = beta
            
        else:
            str = A
            list = str.split("->")
            list = [list[0]] + list[1].split(".")
            if len(list) != 3:
                print("error in item "+str(list))
            self.A = list[0].strip()
            self.Alpha = list[1].split(" ")
            self.Beta = list[2].split(" ")
        if verbose:
            print("correctly constructed item")
            print(self.__str__())
    def __str__(self):
        return self.A+" -> "+" ".join(self.Alpha) +" . "+ " ".join(self.Beta)
    def __repr__(self):
        return repr(self.__str__())
    def __eq__(self,other):
        return self.A == other.A and self.Alpha == other.Alpha and self.Beta == other.Beta
class Rule:
    def __init__(self, A, C=None):
        if C != None:
            self.A = A
            self.C = C
        else:
            list = A.split("->")
            if len(list) < 2:
                print("error in rule "+str(list))
            elif verbose:
                print("correctly read rule: "+list.__str__());
            self.A = list[0].replace(" ","")
            self.C = list[1].strip().split(" ")
            if verbose:
                print("Resulting in:",self.A,"->",self.C)
                print("---")
    def __str__(self):
        return self.A + " -> " + " ".join(self.C)
    def __repr__(self):
        return self.A + " -> " + " ".join(self.C)
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
        self.EOF = None
        self.NUT = set()
        
        self.waitingFirst = set()
        self.waitingFollow = set()
        self.EPSILON = "_"
        self.firstCache = {}
        self.followCache = {}
        self.firstSymbolsCache = {}
        self.ll1table = dict()
        self.ll1condition = None
        
        self.slrcollection = list()
        self.transitiontable = dict()
        self.actiontable = dict()
        self.stateOrigin = [""]
        self.slr1condition = None
        
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
        if verbose:
            print("Adding",str)
        newrule = Rule(str)
        if not self.ruleset:
            self.Axiom = newrule.A
            self.EOF = newrule.C[-1]
        if not newrule.A in self.ruleset:
            self.ruleset[newrule.A] = set()
            self.N.add(newrule.A);
        if not newrule in self.ruleset[newrule.A]:
            self.ruleset[newrule.A].add(newrule)
            self.rulelist.append(newrule)
        self.NUT.add(newrule.A)
        self.NUT.update(newrule.C)
        if self.EPSILON in self.NUT:
            self.NUT.remove(self.EPSILON)
        if self.EOF in self.NUT:
            self.NUT.remove(self.EOF)
        self.T = self.NUT - self.N;
        if verbose:
            print("Terminal",self.T)
            print("NonTerminal",self.T)
        
    def ruleByNumber(self, n):
        return self.rulelist[n]
    
    def first(self, N):
        if " ".join(N) in self.firstCache:
            ret = self.firstCache[" ".join(N)]
        else:
            self.waitingFirst = set()
            ret = set();
            for c in N:
                lastSymFirst = self.first_aux(c)
                ret.update(lastSymFirst)
                if not self.EPSILON in lastSymFirst:
                    if self.EPSILON in ret:
                        ret.remove(self.EPSILON)
                    break
            self.firstCache[" ".join(N)] = ret
        return ret;
    
    def first_aux(self, N):
        if not N or N == self.EPSILON:
            return {self.EPSILON}
        if N in self.T or N == self.EOF:
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
            self.followCache[N] = ret
        return ret
    
    def follow_aux(self,N):
        ret = set()
        if not N in self.waitingFollow:
            if verbose:
                print("-"*len(self.waitingFollow),end='')
                print("Called SIG("+N+")")
            self.waitingFollow.add(N)
            for k in self.ruleset: # for each k in NonTerminals
                for r in self.ruleset[k]: # for each rule of k
                    if N in r.C: # if contains the object of follow
                        if verbose:
                            print("-"*len(self.waitingFollow),end='')
                            print(r)
                        #conc = "".join(r.C) # this is a single string?Shouldnt. It should be a list of string
                        conc = r.C # now it is a list of string
                        #i = conc.find(N) #this works for the string
                        for i, s in enumerate(conc):
                            if s == N:
                                if verbose:
                                    print("-"*len(self.waitingFollow),end='')
                                    print(N,"found in",conc,"at",i)
                                sigstr = conc[i+1:]
                                if sigstr:
                                    ret.update(self.first(sigstr))
                                else:
                                    ret.update(self.follow_aux(k))
                                if self.EPSILON in ret:
                                    ret.remove(self.EPSILON)
                                    ret.update(self.follow_aux(k))
                        '''while i != -1:
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
                            i = conc.find(N)'''
        if verbose:
            print("-"*len(self.waitingFollow),end='')
            print("SIG("+N+") = ",end='')
            print(ret)
        return ret
    
    def firstSymbols(self,rule):
        ret = set()
        if str(rule).isdigit():
            rule = self.ruleByNumber(int(rule))
        if rule in self.firstSymbolsCache:
            ret = self.firstSymbolsCache[rule]
        else:
            conc = rule.C
            ant = rule.A
            ret = self.first(conc)
            if self.EPSILON in ret:
                ret.remove(self.EPSILON)
                ret.update(self.follow(ant))
            self.firstSymbolsCache[rule] = ret
        return ret
    
    def closure(self, J):
        if verbose:
            print("closure of ",J)
        ret = J
        i = 0
        while i < len(ret):
            if verbose:
                print("closing",ret[i])
            item = ret[i]
            if item.Beta:
                a = item.Beta[0]
                if a in self.N:
                    for rule in self.ruleset[a]:
                        if rule.C[0] == self.EPSILON:
                            newitem = LR0Item(rule.A,rule.C,[])
                        else:
                            newitem = LR0Item(rule.A,[],rule.C)
                        if not newitem in ret:
                            if verbose:
                                print("added",newitem)
                            ret = ret + [newitem]
            elif verbose:
                print("Item completo")
            i+=1
        return ret
    def transition(self,J,t):
        ret = list()
        for item in J: # for each item in J
            if verbose:
                print("Called transition("+str(item)+","+t+")")
            if len(item.Beta) > 0 and item.Beta[0]==t: # if after the dot there is the transition symbol
                if verbose:
                    print("will construct with (",item.A,",",str(item.Alpha+[item.Beta[0]]),",",str(item.Beta[1:]),")")
                newitem = LR0Item(item.A,item.Alpha+[item.Beta[0]],item.Beta[1:]) # we move the point
                if verbose:
                    print("transitates to",newitem)
                if not newitem in ret: # and if it is not already in the return
                    ret.append(newitem) # we add it
        return ret
    def isInSLRCollection(self,I):
        ret = False
        stn = -1
        for st in self.slrcollection: # in each state stored
            stn += 1
            sameSt = True
            for ci in I: # in each item of the checked state
                if not ci in st: # if the item is not in the stored state
                    sameSt = False # they are not equal
                    break
            if sameSt: # if every ci is in st, they are the same state
                ret = True
                break;
        if ret == True:
            ret = stn
        return ret
    def makeSLRcollection(self):
        if not self.slrcollection:
            self.slrcollection = [self.closure([LR0Item(self.rulelist[0].A,[],self.rulelist[0].C)])]
            stn = 0
            if verbose:
                print("I0:",self.slrcollection)
            while stn < len(self.slrcollection):
                st = self.slrcollection[stn]
                for s in self.NUT:
                    newState = self.transition(st,s)
                    if newState: # if the transition is valid
                        nextState = self.isInSLRCollection(newState)
                        if nextState == False: # if the state is new
                            if verbose:
                                print("I"+str(stn),"transitates with",s,"to new state I"+str(len(self.slrcollection)))
                            self.stateOrigin.append("transition(I"+str(stn)+","+s+")")
                            self.transitiontable[stn,s] = len(self.slrcollection)
                            self.slrcollection.append(self.closure(newState))
                        else: # if it exists
                            if verbose:
                                print("I"+str(stn),"transitates with",s,"to I"+str(nextState))
                            self.transitiontable[stn,s] = nextState
                    else: # if the transition is not valid
                        self.transitiontable[stn,s] = None   
                stn += 1
    def makeTableOfActions(self):
        self.makeSLRcollection()
        if not self.actiontable:
            accepter = LR0Item(self.Axiom,self.rulelist[0].C[:-1],[self.EOF])
            for i in range(0,len(self.slrcollection)):
                if verbose:
                    print("Actions for state",i)
                for s in self.T.union({self.EOF}):
                    self.actiontable[i,s] = []
                    if s != self.EOF and self.transitiontable[i,s]:
                        if verbose:
                            print(i,"and",s,"transitate to",self.transitiontable[i,s],"so action is D")
                        self.actiontable[i,s].append("D")
                for item in self.slrcollection[i]:
                    if not item.Beta or item.Beta == self.EPSILON: # if there is a final item
                        if verbose:
                            print("Final item found:",item)
                        rulstr = item.A + " -> " + " ".join(item.Alpha)
                        rulered = Rule(item.A,item.Alpha) # we guess the rule
                        if verbose:
                            print("Searching for index of rule:",rulered)
                        for index, rule in enumerate(self.rulelist): # we find it's position in the list
                            if rule == rulered:
                                if verbose:
                                    print("Action is R"+str(index),"in follow of",rule.A,"which is",self.follow(rule.A))
                                for s in self.follow(rule.A):
                                    self.actiontable[i,s].append("R"+str(index)) # the action is the reduction with it
                if accepter in self.slrcollection[i]:
                    if verbose:
                        print(i,"Accepter found:",accepter,"so action is A")
                    self.actiontable[i,self.EOF].append("A")

    def SLR1condition(self):
        self.makeTableOfActions()
        if self.slr1condition == None:
            ret = True
            for i,t in self.actiontable:
                if len(self.actiontable[i,t]) > 1:
                    ret = False
                    break
            self.slr1condition = ret
        return self.slr1condition
    def SLR1analysis(self,cad):
        if self.SLR1condition():
            stack = [0]
            cad = list(cad)
            error = False
            accepted = False
            counter = 1
            while not error and stack and cad and not accepted:
                print(counter,"---")
                print("left:",cad)
                print("stack:",stack)
                counter += 1
                Ix = stack[0]
                a = cad[0]
                action = self.actiontable[Ix,a]
                if not action:
                    print("No match in table of actions")
                    error = True
                else:
                    action = action[0]
                    if action[0] == "D":
                        print("Transition with I"+str(Ix),"and",a,"to I"+str(self.transitiontable[Ix,a]))
                        stack = [self.transitiontable[Ix,a]] + [a] + stack
                        cad = cad[1:]
                    elif action[0] == "R":
                        rule = self.ruleByNumber(int(action[1:]))
                        print("Reduction with rule",rule)
                        if rule.C[0] == self.EPSILON:
                            aux = 0
                        else:
                            aux = 2*len(rule.C)
                        
                        if rule.C[::-1] == stack[1:aux:2] or rule.C[0] == self.EPSILON:
                            stack = [rule.A] + stack[aux:]
                            dest = self.transitiontable[stack[1],rule.A]
                            if dest:
                                stack = [dest]+stack
                            else:
                                print("No transition with I"+stack[1],"and",rule.A)
                                error = True
                        else:
                            print("Expected",rule.C,"to reduce, insted got",stack[1:aux:2])
                            error = True;
                    elif action[0] == "A":
                        print("State I"+str(Ix),"expects the EOF, which is",self.EOF)
                        print("Strings belongs to the language")
                        accepted = True
                    else:
                        print("Unknown action",action)
                        error = True
            if error:
                print("String not recognized")
                print("left:",cad)
                print("stack:",stack)
        else:
            print("Can't analyze with SLR(1): conflicts in table of actions.")
    def LL1(self, N, T):
        ret = list()
        if (N,T) in self.ll1table:
            ret = self.ll1table[N,T]
        else:
            for ind,rule in enumerate(self.rulelist):
                if rule.A == N and T in self.firstSymbols(str(ind)):
                    ret.append(rule.C)
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
            self.ll1condition = ret
        return self.ll1condition
    def LL1analysis(self,cad):
        if self.LL1condition():
            stack = list([self.Axiom])
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
                        print(x,"->",alpha[0])
                        if alpha[0][0] != self.EPSILON:
                            stack = alpha[0] + stack[1:]
                        else:
                            stack = stack[1:]
                elif x in self.T or x == self.EOF:
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
                print("left:",cad)
                print("stack:",stack)
            else:
                print("Strings belongs to the language.")
        else:
            print("LL(1) condition not satisfied")
            return None

    def dumpCollection(self):
        ret = ""
        if not self.slrcollection:
            self.makeSLRcollection()
        for i in range(0,len(self.slrcollection)):
            ret += "\nI"+str(i)+" "+self.stateOrigin[i]+"\n----------------\n"+"\n".join([str(x) for x in self.slrcollection[i]])+"\n"
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
    def dumpFirstSymbols(self):
        ret = ""
        for index in range(len(self.rulelist)):
            ret += "{:<6}".format("SD("+str(self.rulelist[index])+")") + " = " + str(self.firstSymbols(str(index))) +"\n"
        return ret
    def dumpAxiom(self):
        return str(self.Axiom)
    def dumpEOF(self):
        return str(self.EOF)
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
        ret += "\n\nEOF\n"
        ret +=   "---\n"
        ret += self.dumpEOF()
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
    
# os.system('figlet -f small CFGWorker')

print("\033[1;38;2;250;50;50m",end='')
print("  ___ ___ _____      __       _           ")
print(" / __| __/ __\ \    / /__ _ _| |_____ _ _ ")
print("| (__| _| (_ |\ \/\/ / _ \ '_| / / -_) '_|")
print(" \___|_| \___| \_/\_/\___/_| |_\_\___|_|  ")
print("\033[0;1m")
print('Context Free Grammar Worker')
print('https://github.com/MiguelMJ/CFGrammarWorker/')
print("\033[0m",end='')
print('............................................')
cmd = ""
g = Grammar()
prompt = "NoGrammar"
while not cmd in {"exit","quit","end"}: # EXIT
    cmd = input("\033[38;2;0;150;0m"+prompt+" >> \033[0m")
    args = cmd.strip().split(" ")
    cmd = args[0].lower()
    if cmd in {"cab","first"}:      # CAB
        for i in args[1:]:
            print(g.first(i))
    elif cmd in {"sig","follow"}:   # SIG
        for i in args[1:]:
            print(g.follow(i))
    elif cmd in {"ll1"}:            # LL1
        if len(args) == 1:
            print(g.LL1condition())
        else:
            g.LL1analysis(args[1:])
    
    elif cmd in {"slr1"}:           # SLR1
        if len(args) == 1:
            print(g.SLR1condition())
        else:
            g.SLR1analysis(args[1:])
    elif cmd in {"cierre","closure","close"}:   # CIERRE
        j = " ".join(args[1:])
        J = list()
        for i in j.split(";"):
            if i:
                item = LR0Item(i)
                J = J + [item]
        if verbose:
            print("J =")
            for i in J:
                print(i)
        print(g.closure(J))
    elif cmd in {"load"}:                       # LOAD
        g.loadFromFile(args[1])
        prompt = args[1]
    elif cmd in {"dump", "print","show"}:       # PRINT
        for what in args[1:]:
            if what.lower() in {"rules"}:                   # RULES
                print(g.dumpRules())
            elif what.lower() in {"sd","fs","firstsymbols"}:# SD
                print(g.dumpFirstSymbols())
            elif what.lower() in {"nonterminals", "n"}:     # N
                print(g.dumpNonTerminals())
            elif what.lower() in {"terminals", "t"}:        # T
                print(g.dumpTerminals())
            elif what.lower() in {"axiom"}:                 # A
                print(g.dumpAxiom())
            elif what.lower() in {"ll1table","ll1"}:        # LL1TABLE
                for n in g.N:
                    for t in g.T:
                        if g.LL1(n,t):
                            print("LL1("+n+","+t+") =",g.LL1(n,t))
            elif what.lower() in {"collection","c"}:        # C
                print(g.dumpCollection())
            elif what.lower() in {"transitiontable","tt"}:  # TRANSITIONTABLE
                g.makeSLRcollection()
                for i in range(0,len(g.slrcollection)):
                    for s in g.NUT:
                        if g.transitiontable[i,s]:
                            print("TT(I"+str(i)+","+s+") =",g.transitiontable[i,s])
            elif what.lower() in {"actiontable","at","ta"}: # ACTIONATABLE
                g.makeTableOfActions()
                for i in range(0,len(g.slrcollection)):
                    for s in g.T.union({g.EOF}):
                        if (i,s) in g.actiontable and g.actiontable[i,s]:
                            print("AT(I"+str(i)+","+s+") =",g.actiontable[i,s])
            else:
                print("No",what,"to print.")
        if len(args) == 1:
            print(g)
    elif cmd == "verbose":                  # VERBOSE
        verbose = not verbose
        print("verbose = "+str(verbose));
    elif cmd.isdigit():
        if int(cmd) < len(g.rulelist):
            print("{:<4}".format("R"+cmd+"."), end='')
            print(g.ruleByNumber(int(cmd))) # NUMBER
        else:
            print("Rules indexed between 0 and "+str(len(g.rulelist)-1))
    elif not cmd in {"exit","quit","end","close"}:  # EXIT
        print("Unknown command")
    
    
    
    
    
    
    
    
    
