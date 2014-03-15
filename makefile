cc=gcc	# the C compiler, if you're using it

	# this is a gnu make extension.  Quite handy.
.PHONY : test clean run

	# graph is the target that runs your Part I against my input.  graph.out
	# is, in this example, the executable, compiled from graph.c (below) NOTE:
	# Do NOT define inFile inside of this file!  I will fill it in in the
	# environment
byHand : byHand.py
	python byHand.py

byGen : byGen.py
	python byGen.py

viewHand : byHand.py
	less byHand.py

viewGen : byGen.py
	less byGen.py

clean :
	-\rm *.dot
	-\rm *.pyc
	-\rm parser.out
	-\rm parsetab.py
