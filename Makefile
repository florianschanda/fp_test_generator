all: fptg_testsuite
	./build_host_validation.py

fptg_testsuite:
	git clone git@github.com:florianschanda/fptg_testsuite.git

lint: style
	@python3 -m pylint --rcfile=pylint3.cfg --reports=no *.py

style:
	@python3 -m pycodestyle *.py
