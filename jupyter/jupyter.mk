#mode?=user
mode?=root

# tornado==5.1.1
pip_modules := tornado jupyter matplotlib

jupyter : 
ifeq ($(mode),user)
	     pip3 install --user $(pip_modules)
else
	sudo pip3 install        $(pip_modules)
endif

