import setuptools

long_description = '''
# Python-solaredge

Python-solaredge (*pysolaredge* for short) is a library for decrypting and
decoding messages from a SolarEdge photo-voltaic installation (solar panels,
optimizers and inverters, mainly). Such an installation normally reports its
statistics to a server operated by SolarEdge.  This libray allows you to decode
the data yourself, and use it how you see fit.
'''

setuptools.setup(
    name="pysolaredge",
    version="0.5.1",
    author="Martijn Grendelman",
    author_email="m@rtijn.net",
    description="Library for decrypting and decoding messages from SolarEdge inverters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tinuzz/python-solaredge",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "pycrypto",
    ],
)
