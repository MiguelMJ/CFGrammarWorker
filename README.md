# CFGrammarWorker
Python program for analyzing context free grammars with LL(1) and SLR(1)

Actually this project is under development

# How to specify grammars and rules
Grammars must be specified in a text file with a rule in each line

* Rules are specified as follows:
  * Antecedent -> Consequent1 Consequent2 ... ConsequentN
  * Note that context free grammars must have a single symbol in the antecedent.
* Every antecedent will be interpreted as a non terminal symbol of the grammar. Each other symbol will be included in the terminal symbols set.
* The antecedent of the first rule will be taken as the axiom of the grammar
* The symbol '_' is used as empty string symbol by default. Soon will be implemented the posibility for the user to change it.

# Commands

* load <file>: loads a grammar from specified file.
* dump: shows the grammar specification in screen.
* cab <string>: calculates the first symbols set of the string
* others: to be implemented
