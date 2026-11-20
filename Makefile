PY := .venv/bin/python
export PYTHONPATH := .

.PHONY: all setup corpus extract test check clean

all: corpus test

setup:
	python3 -m venv .venv
	$(PY) -m pip install -q -r requirements.txt

# L0: manifest -> biên dịch 60 binary -> sinh 1.000 vector -> kiểm tra chất lượng corpus
corpus:
	$(PY) tools/write_manifests.py
	$(PY) -m vera.corpus.build
	$(PY) -m vera.corpus.vectors
	$(PY) -m vera.corpus.check

# L1: pseudocode (Ghidra headless, một backend cho cả lượt chạy) + evidence cho V3
extract:
	$(PY) -m vera.extract.pseudocode
	$(PY) -m vera.extract.evidence

check:
	$(PY) -m vera.corpus.check

test:
	$(PY) -m pytest -q tests

clean:
	rm -rf build
