install jupyter environment
====================

* make will install jupyter notebook and kernels

```
inst_jupyter$ make -n
cd jupyter && make -f jupyter.mk
cd c && make -f c.mk
cd ocaml && make -f ocaml.mk
cd vpython && make -f vpython.mk
cd sos && make -f sos.mk
```

* c : C and shell kernel
* ocaml : OCaml
* vpython : visual python
* sos : script of script (multiple kernels in one page)

* ocaml and sos simply install packages by pip

* c and vpython install extended/bug-fixed kernels

* if you need only some of them, edit this line
```
subdirs := jupyter c ocaml vpython sos
```

* you can choose whether you install it via root (sudo pip3 install ...) or via regular user (pip3 install --user ...) by changing the following lines in each .mk file (c/c.mk, ocaml/ocam.mk, vpython/vpython.mk and sos/sos.mk)

```
#mode?=user
mode?=root
```
