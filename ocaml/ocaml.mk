#mode?=user
mode?=root

all : ocaml

include ../jupyter/jupyter.mk

ocaml : jupyter
#	opam depext conf-m4.1 conf-pkg-config.1.1 conf-zmq.0.1 conf-gmp.1 conf-zlib.1
	sudo apt install -y m4 pkg-config libzmq3-dev libffi-dev libgmp-dev zlib1g-dev
	echo "" | opam init
	opam install jupyter
	opam install jupyter-archimedes
	ocaml-jupyter-opam-genspec
#	opam install iocaml-kernel
ifeq ($(mode),user)
	~/.local/bin/jupyter kernelspec install --user --name ocaml-jupyter $$(opam var share)/jupyter
#	~/.local/bin/jupyter kernelspec install --user --name ocaml-jupyter ~/.opam/system/share/jupyter
else
#	sudo jupyter         kernelspec install        --name ocaml-jupyter ~/.opam/system/share/jupyter
	sudo jupyter         kernelspec install        --name ocaml-jupyter $$(opam var share)/jupyter
endif
