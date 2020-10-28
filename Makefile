#subdirs := jupyter c ocaml vpython sos
subdirs := jupyter c sos
targets := $(addsuffix /OK,$(subdirs))

all : $(targets)

$(targets) : %/OK :
	cd $* && make -f $*.mk
