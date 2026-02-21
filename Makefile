.PHONY: install run run-all optimize optimize-local test clean

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python main.py

run-all:
	. venv/bin/activate && python test.py

optimize:
	. venv/bin/activate && python app.py

optimize-local:
	. venv/bin/activate && python local.py

test:
	. venv/bin/activate && python -m pytest

clean:
	rm -rf venv __pycache__ *.pyc *.pyo *.log
	bash compiled_files_cleanup.sh
