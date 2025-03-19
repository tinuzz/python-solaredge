# Python-solaredge

## 2024 update

The following note was largely shamelessly stolen from https://github.com/jbuehl/solaredge/,
because it is equally true for this library.

When this project was started, SolarEdge inverters communicated with their monitoring
server using a proprietary data format that was sent in the clear. It was possible to
reverse engineer most of the messages in order to obtain the optimizer level data which
was not otherwise available. The same data was also available on the RS232 and RS485
interfaces which were provided on their inverters. A few years later, SolarEdge
implemented a homegrown encryption algorithm for the communications to their monitoring
server, which prevented access for a while until an effort by a number of contributors
to this project was successful in figuring out the algorithm which got it working again.

In the years since then, SolarEdge has introduced new products which no longer support
the RS232 interface, and they have dropped their encryption algorithm and are now using
the far more secure and mainstream SSL/TLS encryption method which is essentially not
hackable. This means that if you have a newer inverter or if the firmware in your older
inverter is up to date, the only way to access performance data is going to be via the
RS485 interface.

This project is now archived, and no development or support of any kind will take place here.

## Introduction

Python-solaredge (*pysolaredge* for short) is a library for decrypting and
decoding messages from a SolarEdge photo-voltaic installation (solar panels,
optimizers and inverters, mainly). Such an installation normally reports its
statistics to a server operated by SolarEdge.  This libray allows you to decode
the data yourself, and use it how you see fit.

This is not an entirely original work. In essence, it is a rewrite of [the
SolarEdge monitoring scripts by Joe Buehl](https://github.com/jbuehl/solaredge/).
There are multiple reasons that J. Buehl's project didn't work for me, and
I wanted to fully understand SolarEdge's protocol. I wanted to have a library, as
minimalistic as possible, to decrypt and decode the messages from my SolarEdge
installation, so I wrote this, using Joe Buehls code as a study guide.

I am very grateful to Joe Buehl and all the contributors to his project for the
work they have done, in particular the reverse engineering of the SolarEdge
protocol and the encryption. Truly remarkable work, that I could never have
done myself.

This library is written in Python3 and tested on Python 3.5 on Debian.

**Status**: alpha. It works, but it's not complete and it needs testing.

It uses a few modules from the standard library: *logging*, *binascii*, *struct*
 and *time*. It has one external dependency:
[pycrypto](https://pypi.org/project/pycrypto/) (*python3-crypto* in Debian).

If you want to use the included module `pysolaredge.peewee` for storing decoded
data in MySQL or PostgreSQL, you also need
[peewee](https://pypi.org/project/peewee/).

## The SolarEdge protocol

A simple SolarEdge installation consists of 3 main types of components:

* solar panels
* optimizers
* an inverter

The inverter is the central part of the installation. It inverts the DC coming
from the optimizers to AC suitable for the electricity grid. The optimizers
report statistics about their performance to the inverter. The inverter
aggregates those stats and normally sends them to the SolarEdge monitoring
portal over an internet connection.

The inverter uses a proprietary binary protocol to send its data to the server.
The protocol consists of various types of *messages*, each with a unique code
or *function*. When a new installation has been communicating with the
SolarEdge server for a few days, an encryption key is negotiated, and from that
moment on, all communication with the server will be encrypted.

All messages have a header and a payload. The header describes the function of
the message, its source, destination and length. The payload is
function-specific.

The most important message functions that this library handles are:

* 0x003d - encrypted message
* 0x0500 - device telemetry
* 0x0503 - temporary key exchange

In the case of an encryped message, the payload is just a whole new message,
which, after decryption, has exactly the same format. In other words, device
telemetry is contained in a 0x0500 message, which is encrypted and then
*wrapped* in a 0x003d message.

Telemetry messages (function 0x0500) contain data from different devices
(optimizers, inverters, batteries) and sometimes events and other data. The
payload of a 0x0500 message is a collection of concatenated sets of device
data, each set identified by a *device ID*. The library parses these messages
and returns the telemetry data in dictionaries, one dictionary per device type.

The messages with function code 0x0503 contain an encrypted temporary key, that
is used to encrypt all subsequent messages, until the key is changed with the
next 0x0503 message. Encryption is done with AES128, which uses a 16-byte key.
The temporary key is a random string of 16 bytes, encrypted with the private
key. This way, the private key (which never changes) doesn't have to be used to
encrypt individual messages, and a form of forward secrecy is obtained, meaning
that even with the private key, you cannot decrypt any past messages if you
didn't capture the temporary key exchange.

## Using this library

To be able to decode and store the data from a SolarEdge installation that was
sent over the network, you need a few things:

* the encrypted data
* the private key that was negotiated in the beginning
* a temporary key that is rotated regularly (every few hours to days), in the
  form of a so-called '0x0503 message'

If the data you have is *not* encrypted, you do not need any key material, of
course. Decoding messages works just the same, in that case.

How to get all of those things, I will cover later. But if you have them, using
this library is as simple as this:

```
import pysolaredge
decoder = pysolaredge.Decoder(privkey = '<your private key>', last_503_msg = '<your last 0x0503 message>')
result = decoder.decode('<message to decode>')
```

The *result* will be a dictionary, whose contents depend on the type of message
you were trying to decode, or an exception if something went wrong. The same
decoder object can be used to decode as many messages as you like. If a 0x0503
message is encountered, the decryption is automatically re-initialized with the
new temporary key.

Take care though: in the case of a 0x0503 message, the decoded payload will not
contain meaningful information, but the entire message will have to be stored
somewhere (in a file, a database or something similar) because it will be
needed every time the decoder is initialized. The library does NOT handle the
storage of 0x0503 messages, that is up to the application using this library.

The Decoder class has only 3 methods meant to be used publicly:

* `set_privkey(privkey)` - set the private key if not done when instantiating
* `set_last_503_msg(msg)` - set the last 0x0503 message, if not done when
  instantiating
* `decode(msg)` - decode a message

Please note that the *last_503_msg* in the context of this package is supposed
to be the *entire* message, starting with the SolarEdge magic sequence (`12 34
56 79`), up to and including the checksum, because the message will be pulled
through the decoder like any other message.

## Getting the private key and the data

[Joe Buehl](https://github.com/jbuehl/solaredge/) has written extensively about
how to get the data from a SolarEdge inverter, so I am not going to copy that
here. By far the easiest and non-intrusive way to get the data, is to passively
sniff it from the network. For that to be possible, the device that you run
your software on, should receive the network packets from the inverter. In my
own home, I run a Linux box as a router for the local network, and the
SolarEdge inverter is on a dedicated VLAN. This makes it easy to sniff the data
with *tcpdump* or *Wireshark*. If this kind of setup is not possible for you, I
can think of a few other ways to passively sniff the data:

* Use a network hub (not a switch) to connect the inverter and your server to
  the rest of the network. A hub will send all traffic to all ports, so you can
  easily sniff it. Network hubs are becoming hard to get, though.
* Use port mirroring on a switch to copy all traffic from the inverter to
  another port on the switch, so you can sniff it there. It takes a managed
  switch to be able to do this, though.
* Use a device like a Raspberry Pi with two ethernet interfaces in a bridge.
  Connect it *in serial* between the inverter and the router. All traffic will
  pass through the bridge and you can sniff it there.

The private key that is used for the encryption will be sent from the inverter
to the SolarEdge server in a couple of messages with function code 0x0090.
These are normally only sent once, so if you do not want to resort to a serial
connection to extract the key from the inverter, it is important to start
storing the network communication from the inverter right from the start.

Please note that the code for extracting the private key with this library has
not been fully implemented yet, so I recommend keeping a dump of all traffic,
at least until you have successfully obtained your private key.

## Storing data in a database with Peewee

[Peewee](http://docs.peewee-orm.com/en/latest/) is a simple and small ORM, that
makes it quite easy to access relational databases. It uses model classes to
map database tables to Python objects.

Pysolaredge includes a module that takes care of the hard part: mapping the
decoded data from the decoder module to columns in a database table. Using it
is quite simple. First, install the Peewee ORM and the database driver of your
choice (MySQL, PostgreSQL and SQLite are supported):

```
pip install peewee mysqlclient
```

Then, import the necessary stuff in your program, initialize the database
and store the data:

```
from peewee import *
from pysolaredge.peewee import db_proxy, Inverter, Optimizer

# Set db, db_user, db_pass and db_host appropriately
dbc = MySQLDatabase(db, user=db_user, password=db_pass, host=db_host)
db_proxy.initialize(dbc)
dbc.connect()
dbc.create_tables([Inverter, Optimizer])

# See decoder usage above!
result = decoder.decode('<message to decode>')

if 'decoded' in result:
    if 'inverters' in result['decoded']:
        for dev_id,inverter in result['decoded']['inverters'].items():
            Inverter.create(**inverter)
    if 'optimizers' in result['decoded']:
        for dev_id,optimizer in result['decoded']['optimizers'].items():
            Optimizer.create(**optimizer)
```

The added value of the `pysolaredge.peewee` module is, that it provides
a database structure that is a one-on-one mapping to the data structure
that is returned by the decoder.

## Integrated solution: Pyp

When I first started working on my SolarEdge scripts, I quickly realised, that
I needed to be able to read from multiple inputs: sniff the network, read from
a file, perhaps even make the inverter talk to my script directly. And even
more importantly, I had no idea where I wanted the data to go: CSV or JSON files,
MySQL database, InfluxDB or Graphite? Soon, I decided my script needed to be
pluggable: input, processing and output should all be done by separate modules
that weren't tightly integrated.

That's when Pyp (pronounce: "pipe") was born.

Pyp is a simple data pipeline. Think of it as an extremely simple version of
Apache Flink or AWS Kinesis.

Pyp comes with a 'solaredge' decoder plugin, that uses Pysolaredge for the
decrypting and decoding. It also stores 0x0503 messages, and reads them back on
startup, so the decryptor can be initialized correctly and pick up decrypting
and decoding where it left off.

Pyp also comes with a few handy input plugins, that make the collection of data
from your SolarEdge inverter quite easy, and there are some output plugins too.
The Pysolaredge library was separated from Pyp, because Pyp turned out to be
quite a generic tool, that can be used for all kinds of data processing, not
just SolarEdge data.

Pyp will be up on Github shorty.

