test:
	python -m unittest discover -s tests -v

quick:
	python software/run_release.py --mode quick --out reproduction_output

nominal:
	python software/run_release.py --mode nominal --out reproduction_output
