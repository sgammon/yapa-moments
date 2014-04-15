
################
#              #
# YAPA MOMENTS #
#              #
################

all: package

## == top-level commands == ##
test:
	@-nosetests --verbose --with-coverage --cover-package=moments test_moments

build: .Python
	@echo "Building Yapa-Moments..."
	@-bin/python setup.py build

package: build
	@echo "Making source distributions..."
	@-bin/python setup.py sdist

	@echo "Making binary/egg distributions..."
	@-bin/python setup.py bdist_egg bdist_dumb

install: package
	@echo "Installing Yapa-Moments..."
	@-bin/python setup.py install

## == deps and virtualenv == ##
deps:
	@echo "Installing Python dependencies..."
	@-bin/pip install -r requirements.txt

.Python:
	@echo "Setting up virtual environment..."
	@-virtualenv .

	@-$(MAKE) deps

## == cleaning routines == ##
clean:
	@echo "Cleaning virtual environment..."
	@-rm -fr bin/ include/ lib/ .Python moments.egg-info

distclean: clean
	@echo "Cleaning untracked files..."
	@-git clean -xdf

	@echo "Resetting codebase..."
	@-git reset --hard
