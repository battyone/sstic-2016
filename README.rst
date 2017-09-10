Solution of SSTIC 2016 challenge, in French
===========================================

This repository contains the scripts and other resources I have used to solve
the computer-security challenge of SSTIC 2016, available at
http://communaute.sstic.org/ChallengeSSTIC2016

It also contains the files needed to generate the report I have written to
describe my solution.  The generated PDF file is available at
http://static.sstic.org/challenge2016/solutions/solution_nicolas_iooss.pdf

I am used to write code and README files in English, so even if the report
describing my solution is written in French, every other file would be written
in English.


Dependencies
------------

To be able to successfully build this project, the following software is needed:

* Usual build tools: ``gcc``, ``g++``, ``make``, ``coreutils``...
* Some archive tools: ``tar``, ``unzip``
* Python 2.7 (for scapy) and 3 (tested with 3.4)
* openssl program to decrypt stages 0, 2 and 4, https://www.openssl.org/
* scapy Python library for stage 3, http://www.secdev.org/projects/scapy/
* Crypto++ C++ library, to decrypt stage 3, http://www.cryptopp.com/
* pillow Python library, for stage 6, http://python-pillow.github.io/

* tshark, Wireshark command-line interface
* xxd, to convert hexadecimal data back to binary, packaged with vim
* dd
* ... cf. Makefile (TODO: use variables to invoke commands)

* python-crypto to use AES in Python

* pandoc, to convert the markdown files into LaTeX files
* LaTeX, to build the solution PDF


Build commands
--------------

* To build everything possible in this repository, type::

    make

* To build the solution PDF::

    make solution.pdf
