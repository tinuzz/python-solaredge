install:
	rsync -avP --delete pysolaredge /usr/local/lib/python3.5/dist-packages

build:
	python3 setup.py sdist bdist_wheel

upload-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload:
	twine upload dist/*

.PHONY: install build upload-test upload
