DOC		= doc
RSL		= results


all: 		test3


test2:
		mpirun -np 4 python ./test.py

test3:
		mpirun -np 4 python3.6 ./test.py


doc:
		@mkdir -p $(DOC)
		doxygen $(DOC)/Doxyfile.in


clean:
		$(RM) -rf $(DOC)/*/* $(RSL)/*


.PHONY:		test2 test3 doc clean


