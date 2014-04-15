# -*- coding: utf-8 -*-

'''

  yapa moments demo: ffmpeg driver

'''

# stdlib
import os
import sys
import traceback
import subprocess

# local
from . import base


class FFmpeg(base.MomentBase):

  ''' Class that wraps and properly handles calls to FFmpeg, related
      to generating :py:class:`moments.api.Moment` videos. Things are
      meant to pass through this to :py:mod:`subprocess`. '''

  __args__ = None  # positional arguments for this ``FFmpeg`` run
  __input__ = None  # stdin input for target ``FFmpeg`` run
  __kwargs__ = None  # keyword arguments for this ``FFmpeg`` run
  __output__ = None  # stdout output for target ``FFmpeg`` run
  __target__ = None  # target subprocess containing ``FFmpeg``
  __moment__ = None  # moment job that we'll be working on this run
  __pending__ = False  # flag that indicates we are actively working

  def __init__(self, moment):

    ''' Initialize an FFmpeg instance, with arguments/config/options.
        Keyword arguments passed here override values from ``self.config``.

        :param moment: :py:class:`Moment` object to compile into a video.
        :returns: Nothing, as this is a constructor. '''

    self.__moment__, self.__args__, self.__kwargs__ = (
      moment,  # target moment
      [], {}  # args and kwargs
    )

  ## == Internals == ##
  def _spawn(self):

    ''' Spawn ``FFmpeg`` subprocess, reducing the current argument set
        into a valid string to be executed by :py:mod:`subprocess`.

        :returns: Target :py:mod:`subprocess.Popen` object. '''

    # generate string command
    command = self._make_command()
    self.logging.debug('Spawning FFmpeg with command: "%s".' % command)

    if not self.__target__:
      self.__target__ = subprocess.Popen(
        self._make_command(),
        bufsize=0  # don't buffer from ffmpeg
      )

    self.logging.debug('FFmpeg running under native driver at PID %s.' % self.__target__.pid)
    return self.__target__

  @property
  def _ffmpeg_path(self):

    ''' Returns the default path to ``FFmpeg``, which is distributed along
        with this package by default. '''

    _default_path = os.path.abspath(
      os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'resources',
        'ffmpeg'
      ))

    self.logging.debug('Using FFmpeg at path: "%s".' % _default_path)
    return _default_path

  def _make_command(self):

    ''' Reduces the current argument set into a valid command to be executed
        by :py:class:`subprocess.Popen`.

        :returns: ``self``, for easy chainability. '''

    try:
      os.stat(self._ffmpeg_path)
    except OSError as e:
      if self.moment.options.debug:
        traceback.print_exception(*sys.exc_info())
      self.logging.critical('Failed to find FFmpeg. Exiting.')
      raise RuntimeError('Cannot find `FFmpeg` executable.')
    else:
      return [self._ffmpeg_path] + self.args + [
          (("--%s" % k) + (("=%s" % v) if v is not None else "")) for k, v in self.kwargs.iteritems()
        ] if self.kwargs else []

  ## == Command Flow == ##
  def _add_argument(self, *positional, **kwargs):

    ''' Add a positional (value-based) argument to the current argset.

        :param positional: ``str`` values to add, positionally. Defaults
        to ``None`` so ``kwargs`` may be passed independently.

        :param kwargs:: ``dict`` representing keyword-mapped arguments
        to add. Can be specified in addition to (or in-place-of) ``positional`` arguments.

        :returns: ``self``, for easy chainability. '''

    # map args
    if positional:
      for argument in positional:
        self.__args__.append(argument)

    # map kwargs
    if kwargs:
      for keyword, argument in kwargs.iteritems():
        self.__kwargs__[keyword] = argument

    return self

  ## == Context Management == ##
  def __enter__(self):

    ''' Spawn the subprocess containing ``FFmpeg`` and switch contexts
        to make sure we can keep track of it. '''

    if self.__pending__:
      raise RuntimeError("Cannot invoke ``FFmpeg`` concurrently.")

    self.__pending__ = True  # indicate pending mode
    return self  # set self as final driver

  def __exit__(self, exc_type, exception, exc_info):

    ''' Handle clean exit for failure and success states after using
        the ``FFmpeg`` subprocess in-context. '''

    if not self.__pending__:
      raise RuntimeError("Out-of-context ``__exit__`` invocation.")

    if exception:
      return False  # @TODO(sgammon): exception suppression? cleanup?
    return True

  def __call__(self, *args, **kwargs):

    '''  '''

    # map final arguments, if any
    if args or kwargs:
      self._add_argument(*args, **kwargs)

    # stdout and stderr output
    stdout, stderr = self.target.communicate(self.__input__ or None)
    return (self.target.returncode, stdout, stderr)

  ## == Property Mappings == ##
  args = property(lambda self: self.__args__)  # args sent to ``FFmpeg``
  kwargs = property(lambda self: self.__kwargs__)  # kwargs sent to ``FFmpeg``
  target = property(lambda self: self._spawn())  # spawn/grab process
  moment = property(lambda self: self.__moment__)  # subject moment
