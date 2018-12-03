# CFGrammarWorker
Python CLI program for analyzing context free grammars with LL(1) and SLR(1). 

Currently this project is under development

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
* `ll1`: tells wether the grammar satisfies the LL(1) condition or not.
* `ll1table`: shows the LL(1) table.
* `verbose`: toggles the verbosity of the processes. It is thought for debugging.
* others to be implemented

