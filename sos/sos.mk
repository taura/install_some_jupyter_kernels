#mode?=user
mode?=root

all : sos

include ../jupyter/jupyter.mk

sos : jupyter
ifeq ($(mode),user)
	sudo apt remove sosreport
	pip3 install --user sos sos-notebook
	python3 -m sos_notebook.install
else
	sudo apt remove sosreport
	sudo pip3 install sos sos-notebook
	sudo python3 -m sos_notebook.install
endif
