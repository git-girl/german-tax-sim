# Same as in CICD
lint:	
	# NOTE: $$ because Makefile
	pylint $$(git ls-files '*.py')

doc: 
	sphinx-apidoc -f -o docs/source .
	@echo "ashdjkl"
	sphinx-build -b html docs/source/ docs/build/html
