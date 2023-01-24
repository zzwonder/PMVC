This directory contains the implementations for Tutte encodings, Enum-Blossom and QBF for FORALL-PMVC as well as the benchmarks used in the experiments.

Requirements
--------------
Python with package pysat, numpy, networkx 

Usage
--------------
Run

	python3 main.py --FORALLPMMethod=[TutteCNF, TuttePBXOR, Blossom, QBF] --graphFile=[Input file encoding a graph] --state=[GHZ, Dicke], --k=[the right-hand-side in Dicke State]
	

For exapmle, run:

	python3 main.py --FORALLPMMethod=TutteCNF --graphFile=example.graph --k=4  --state=Dicke
	
The results reveal that the graph encoded by example.graph violates the FORALL-PMVC condition for k=4.

As an another example, run:

	python3 main.py --FORALLPMMethod=TutteCNF --graphFile=cycle.graph --state=GHZ
	
The results reveal that the cycle satisies the GHZ state.

Set --breakSymmetry=False to disable the optimization techniques of Tutte encoding.

Benchmarks
----------------
The graphs used in the three experiments can be found in ./benchmarks

Alternative Constraint-Satisfiability Solvers
---------------------------------------------
To use an alternative SAT/PB/QBF solver, put the solver in ./solvers and modify the solver path in Configuration class in main.py.


Clingo Implementations
-----------------------
We also implemented the Tutte encoding in Clingo, an ASP platform. In ./clingo, run

	./clingo Dicke.lp
	
The results reveal that no such Tutte set can be found and DickeGraph(10,4) satisfies the Dicke FORALL-PMVC condition.
