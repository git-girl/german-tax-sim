# Same as in CICD
lint:	
	# NOTE: $$ because Makefile
	pylint $$(git ls-files '*.py')
