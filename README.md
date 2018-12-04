# CFGrammarWorker
Python CLI program for analyzing context free grammars with LL(1) and SLR(1). 

# How to specify grammars and rules
* Grammars must be specified in a text file with a rule in each line
* Rules are specified as follows:
  * Antecedent -> Consequent1 Consequent2 ... ConsequentN
  * Note that context free grammars must have a single symbol in the antecedent.
* Every antecedent will be interpreted as a non terminal symbol of the grammar. Each other symbol will be included in the terminal symbols set.
* The antecedent of the first rule will be taken as the axiom of the grammar.
* The symbol '_' is reserved. It is used as empty string symbol by default.

# Commands

For those not used to this notation: `|` separates two equivalent options, `<field>` is an obligatory filed and `[field]` is an optional field.

Command recognition is not case sensitive.

* `load <file>`: loads a grammar from specified file. It should be the first command to be called.
* `dump|print [rules] [sd|fs|firstsymbols] [nonterminals|N] [terminals|T] [axiom]`: shows the grammar specification in screen.
* `cab|first <cad>`: calculates the first symbols set of the string.
* `sig|follow <cad>` <NonTerminal>: calculates de following symbols set of the non terminal symbol.
* `sd|fs|firstsymbols <cad>` <number>: calculates the set of first symbols of the rule indexed with that number. To see the rules index, use `dump rules`.
* `ll1 [s1] [s2] ... [sn]`: If no arguments are given, it just tells wether the garmmar satisfies the LL(1) condition. Otherwise, and if the grammar is LL(1), it evaluates the string that the arguments form.
* `ll1table`: shows the LL(1) table.
* `verbose`: toggles the verbosity of the processes. It is thought for debugging.
* others to be implemented
 
 # Contribute
 
Currently this project is under development. I know the code is not as pythonic as it could be, so I hope to clean it a bit soon. The program does not handle errors properly yet neither, that's another thing to be implemented. Also, it requires more exhaustive testing, so if you find any issues, feel free to report it.
