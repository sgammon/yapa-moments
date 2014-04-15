
################
#              #
# YAPA MOMENTS #
#              #
################

# settable configuration


# environment configuration

all: package

deps:
	@echo "Installing Python dependencies..."
	@-bin/pip install -r requirements.txt

.Python:
	@echo "Setting up virtual environment..."
	@-virtualenv .

	@-$(MAKE) deps

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

