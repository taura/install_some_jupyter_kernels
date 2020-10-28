subdirs := jupyter c ocaml vpython sos
targets := $(addsuffix /OK,$(subdirs))

all : $(targets)

$(targets) : %/OK :
	cd $* && make -f $*.mk
