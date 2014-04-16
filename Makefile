
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
deps: .Python resources/ffmpeg resources/samples
	@echo "Installing Python dependencies..."
	@-bin/pip install -r requirements.txt

.Python:
	@echo "Setting up virtual environment..."
	@-virtualenv .
	@-$(MAKE) deps

resources/ffmpeg:
	@echo "Downloading bundled FFmpeg..."
	@-curl -L --progress-bar http://storage.googleapis.com/mm-bullpen/ffmpeg.tar.gz > resources/ffmpeg.tar.gz

	@echo "Extracting bundled FFmpeg..."
	@-cd resources/; \
		tar -xf ffmpeg.tar.gz;

resources/samples:
	@echo "Extracting sample images..."
	@-cd resources/; \
		tar -xvf samples.tar.gz;

## == cleaning routines == ##
clean:
	@echo "Cleaning virtual environment..."
	@-rm -fr bin/ include/ lib/ .Python moments.egg-info

distclean: clean
	@echo "Cleaning untracked files..."
	@-git clean -xdf

	@echo "Resetting codebase..."
	@-git reset --hard
