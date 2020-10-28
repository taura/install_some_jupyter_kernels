all : vpython

include ../jupyter/jupyter.mk

#mode?=user
mode?=root

vpython : jupyter
	sudo rm -rf vpython-jupyter
	git clone https://gitlab.eidos.ic.i.u-tokyo.ac.jp/thiguchi/vpython-jupyter
ifeq ($(mode),user)
	cd vpython-jupyter &&      python3 setup.py install --user
else
	cd vpython-jupyter && sudo python3 setup.py install
endif

