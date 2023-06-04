run: 
	@conda run -n german-tax-sim python german_tax_sim.py
# Same as in CICD
lint:	
	# NOTE: $$ because Makefile
	@conda run pylint $$(git ls-files '*.py')

doc: 
	sphinx-apidoc -f -o docs/source .
	@echo "ashdjkl"
	sphinx-build -b html docs/source/ docs/build/html
