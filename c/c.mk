#mode?=user
mode?=root

all : c_kernel

include ../jupyter/jupyter.mk

c_kernel : jupyter
ifeq ($(mode),user)
	LC_ALL=C pip3 install --user jupyter-c-kernel
	~/.local/bin/jupyter kernelspec install --user c_kernel
	cp --backup patched_c_kernel.py $$(python3 -c 'import jupyter_c_kernel,os; print(os.path.dirname(jupyter_c_kernel.__file__))')/kernel.py
else
	LC_ALL=C sudo pip3 install jupyter-c-kernel
	sudo jupyter kernelspec install c_kernel
	sudo cp --backup patched_c_kernel.py $$(python3 -c 'import jupyter_c_kernel,os; print(os.path.dirname(jupyter_c_kernel.__file__))')/kernel.py
endif
