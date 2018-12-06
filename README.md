# CFGrammarWorker
Python CLI program for analyzing context free grammars with LL(1) and SLR(1).
# Usage
## How to specify grammars and rules
* Grammars must be specified in a text file with a rule in each line.
* Rules are specified as follows:
  * Antecedent -> Consequent1 Consequent2 ... ConsequentN
  * Note that context free grammars must have a single symbol in the antecedent.
* Every antecedent will be interpreted as a non terminal symbol of the grammar. Each other symbol will be included in the terminal symbols set.
* The antecedent of the first rule will be taken as the axiom of the grammar. The last symbol of the first rule, will be taken as the end of sentence.
* The symbol `_` is reserved. It is used as the empty string metasymbol.
* The symbols `.` and `;` are not reserved, but will cause conflicts with the command `cierre|closure|close`. It won't conflict with `slr1`, though. This is because the first command must interpret a set of strings a LR(0) items, while the second one just builds them internally.

## Commands

For those not used to this notation: `|` separates two equivalent options, `<field>` is an obligatory filed and `[field]` is an optional field.

Command recognition is not case sensitive.

* `load <file>`: loads a grammar from specified file. It should be the first command to be called. The name of the current loaded grammar will be shown in the prompt.
* `dump|print|show [rules] [sd|fs|firstsymbols] [nonterminals|n] [terminals|t] [axiom] [ll1|ll1table] [collection|c] [transitiontable|tt] [actiontable|at|ta]`: shows the grammar specification in screen.
* `cab|first <s1> <s2> ... <sn>`: calculates the first symbols set of the string formed by the arguments.
* `sig|follow <nt>`: calculates de following symbols set of the non terminal symbol.
* `ll1 [s1] [s2] ... [sn]`: If no arguments are given, it just tells wether the garmmar satisfies the LL(1) condition. Otherwise, and if the grammar is LL(1), it evaluates the string that the arguments form.
* `cierre|closure|close <item1>; <item1>; ... ;<itemn>`: calculates the closure set of the one provided. To specify the LR(0) items, do as with the rules and separating alpha and beta with a dot `.`. Also, separate each item with `;`
* `slr1 [s1] [s2] ... [sn]`: SLR(1) alternative to `ll1`. I checks the action table instead.
* `verbose`: toggles the verbosity of the processes. It is thought for debugging.
* `exit|end|quit` to exit the program.
* Writing just a number will print the rule indexed with it, if there is one.

# Contribute
 
Currently this project is under development. I know the code is not as pythonic as it could be, so I hope to clean it a bit soon. The program does not handle errors properly yet neither, that's another thing to be implemented. Also, it requires more exhaustive testing, so if you find any issues, feel free to report it.

# Credits

Thanks to [nightroy](https://github.com/nightroy99) for his support and contributing with the correct specification of the `first` algorithm.
