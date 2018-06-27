install:
	rsync -avP --delete pysolaredge /usr/local/lib/python3.5/dist-packages

build:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel

upload-test:
	twine upload -r testpypi dist/*

upload:
	twine upload dist/*

.PHONY: install build upload-test upload
