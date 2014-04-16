# -*- coding: utf-8 -*-

'''

  yapa moments demo: API

'''

# stdlib
import os
import sys
import pdb
import glob
import traceback
import collections

# local
from . import base, driver


class MomentOptions(object):

  ''' Stores configuration options for a single :py:class:`Moment`
      instance and production run. '''

  ## Input/Output
  __source__ = None  # source images - glob or directory string
  __target__ = None  # video target - where to put the finished video

  ## Options
  __dbg__ = False  # whether debug mode is enabled (defaults to `False`)
  __quiet__ = None  # optionally suppress most application output
  __verbose__ = None  # optionally add additional application output
  __audio__ = None  # either `False` (for no audio) or a string path to audio file

  def __init__(self, **options):

    ''' Initialize a :py:class:`MomentOptions` object or subclasses object
        by setting internal attributes according to ``**options``.

        :param options: Kwargs-style rollup that applies all properties to
        their internal representations.

        :returns: Nothing, as this is a constructor. '''

    for option, value in options.iteritems():
      setattr(self, ('__%s__' % option) if option != 'debug' else '__dbg__', value)

  ## == Property Mappings == ##
  source = property(lambda self: self.__source__)
  target = property(lambda self: self.__target__)
  audio = property(lambda self: self.__audio__)
  debug = property(lambda self: self.__dbg__)
  quiet = property(lambda self: self.__quiet__)
  verbose = property(lambda self: self.__verbose__)


class Moment(base.MomentBase):

  ''' Class representing an individual ``moment`` (a slideshow video),
      generated from a set of images. '''

  __source__ = None  # actual handles to source images (not config, like above)
  __target__ = None  # actual handle to output video (not config, like above)
  __driver__ = None  # driver to `ffmpeg`
  __options__ = None  # additional options that were set upon invocation

  ## Descriptors
  __stdin__, __stdout__, __stderr__ = None, None, None  # standard in, out and err

  def __init__(self, source, target, _driver=None, **options):

    ''' Initialize a new :py:class:`Moment` with configuration and
        details.

        :param source: Glob or string path to a directory full of images.
        :param target: String destination path for the resulting video.
        :param driver: Replacement ``driver`` to use in place of :py:class:`driver.FFmpeg`.
        :returns: Nothing, as this is a constructor. '''

    # mount options and spawn driver
    self.__options__ = MomentOptions(source=source, target=target, **options)
    self.__driver__ = (_driver or driver.FFmpeg)(self)
    self.__source__ = collections.deque()

  ## == Internals == ##
  def _validate_input(self, source=None):

    '''  '''

    for input_item in glob.iglob(source or self.options.source):

      try:
        os.stat(input_item)
      except:
        if self.options.debug: pdb.set_trace()
        self.logging.critical('Moment tool encountered fatal error scanning input item'
                              ' "%s" and will now exit.' % input_item)
      else:
        self.logging.info('Found valid source image "%s"...' % input_item)
        self.__source__.append(input_item)
    return self

  def _validate_output(self, target=None):

    '''  '''

    target = target or self.options.target

    try:
      os.stat(os.path.dirname(target))
    except:
      if self.options.debug: pdb.set_trace()
      self.logging.critical('Moment tool encountered fatal error scanning output target,'
                            ' and will now exit.')
      raise
    else:
      self.logging.info('Tested valid output path "%s"...' % target)
    self.__target__ = target  # set local target
    return self

  ## == Public == ##
  def __call__(self, stdin, stdout, stderr):

    '''  '''

    # map file descriptors
    self.__stdin__, self.__stdout__, self.__stderr__ = (
      stdin, stdout, stderr
    )

    # check input and gather files
    if self._validate_input() and self._validate_output():
      self.logging.info('Creating new Moment from %s input images...' % len(self.source))

      # acquire driver and start working
      with self.driver as ffmpeg:

        args = [

          "-r 1",                        # input rate
          "-pattern_type glob",          # enable input globs
          "-i",                          # input flag
          '"%s"' % self.options.source,  # space-separated image paths
          "-c:v",                        # ???
          "libx264",                     # output muxer
          "-r 30",                       # output rate
          "-pix_fmt yuv420p",            # picture format
          self.target                    # output video location

        ]

        ffmpeg(*args)

    else:
      self.logging.critical("Input files failed validation. Exiting.")

    return False  # run failed

  ## == Property Mappings == ##
  source = property(lambda self: self.__source__)  # source image file handles
  target = property(lambda self: self.__target__)  # target video file handle

  stdin = property(lambda self: self.__stdin__)  # standard in
  stdout = property(lambda self: self.__stdout__)  # standard out
  stderr = property(lambda self: self.__stderr__)  # standard err

  driver = property(lambda self: self.__driver__)  # mapped ffmpeg driver
  options = property(lambda self: self.__options__)  # configuration options
