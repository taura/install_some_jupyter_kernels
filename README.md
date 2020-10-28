install jupyter environment
====================

* Just run "make" at the toplevel directory and it will install jupyter notebook and kernels

```
install_some_jupyter_kernels$ make
cd jupyter && make -f jupyter.mk
cd c && make -f c.mk
cd sos && make -f sos.mk
```

Folders
====================

* `c` : C and shell kernel, extended https://github.com/brendan-rius/jupyter-c-kernel including some bug fixes)
* `ocaml` : OCaml 
* `vpython` : visual python
* `sos` : script of script (multiple kernels in one page) https://vatlab.github.io/sos-docs/

`ocaml` and `sos` simply install packages by pip
`c` and `vpython` install extended/bug-fixed kernels

Selecting kernels
====================

if you need only some of them, edit this line in the Makefile

```
#subdirs := jupyter c ocaml vpython sos
subdirs := jupyter c sos
```

By default only C and sos will be installed.

Root install vs user install
====================

You can choose whether you install it as root (sudo pip3 install ...) or as a regular user (pip3 install --user ...) by changing the following lines in each .mk file (c/c.mk, ocaml/ocam.mk, vpython/vpython.mk and sos/sos.mk)

```
#mode?=user
mode?=root
```
