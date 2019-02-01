DOC		= doc
DAT		= data

all: 		test

test:
		mpirun -np 4 python3.6 ./test.py

doc:
		@mkdir -p $(DOC)
		doxygen $(DOC)/Doxyfile.in

package:
		tar czvf ../shardSim.tgz ./* --exclude-vcs --exclude='*.pyc'

clean:
		$(RM) -rf $(DOC)/*/* $(DAT)/*

.PHONY:		test doc clean


