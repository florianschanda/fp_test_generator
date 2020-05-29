all: fptg_testsuite
	./build_host_validation.py

fptg_testsuite:
	git clone git@github.com:florianschanda/fptg_testsuite.git
