# -*- coding: utf-8 -*-

'''

  yapa moments demo: ffmpeg driver

'''

# stdlib
import os
import sys
import shutil
import tempfile
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
  __scratch__ = None  # scratch directory where temp files can be written
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

    if not self.__target__:
      self.logging.debug('Spawning FFmpeg with command: "%s".' % ' '.join(command))

      self.__target__ = subprocess.Popen(
        command,
        shell=False,
        bufsize=0,  # don't buffer from ffmpeg
        executable=self._ffmpeg_path
      )
      self.logging.debug('FFmpeg running under native driver at PID %s.' % self.__target__.pid)
    return self.__target__

  def _provision_scratchspace(self):

    ''' Provision a temporary directory to write midway input image
        files, after resizing/reformatting. This is called during
        context entry on the :py:class:`FFmpeg` driver.

        :returns: The string location of the new scratch directory,
        which is also stored at ``self.__scratch__``. '''

    # allocate a temp directory and return
    space = tempfile.mkdtemp()
    if self.moment.options.verbose:
      self.logging.debug('Provisioned scratchspace at location "%s".' % space)
    return setattr(self, '__scratch__', space) or self.__scratch__

  def _destroy_scratchspace(self):

    ''' Destroy temporary scratch space originally allocated at the
        beginning of the run to save midway image source files.

        :raises OSError: If an ``OSError`` is encountered with an
        error code other than ``2``.

        :returns: Nothing. '''

    space = self.__scratch__

    if self.moment.options.verbose:
      self.logging.debug('Destroyed scratchspace at location "%s".' % space)
    try:
      #shutil.rmtree(space)
      pass
    except OSError as e:
      if e.errno != 2:  # code 2 == no such file or directory
        raise

  @property
  def _ffmpeg_path(self):

    ''' Calculates the default path to ``FFmpeg``, which is distributed along
        with this package by default.

        :returns: String path to ``FFmpeg`` binary. '''

    _default_path = os.path.abspath(
      os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'resources',
        'ffmpeg'
      ))

    return _default_path

  def _make_command(self):

    ''' Reduces the current argument set into a valid command to be executed
        by :py:class:`subprocess.Popen`.

        :returns: ``self``, for easy chainability. '''

    path = self._ffmpeg_path

    if self.moment.options.debug:
      self.logging.debug('Using FFmpeg at path: "%s".' % path)

    try:
      os.stat(path)
    except OSError:
      if self.moment.options.debug:
        traceback.print_exception(*sys.exc_info())
      self.logging.critical('Failed to find FFmpeg. Exiting.')
      raise RuntimeError('Cannot find `FFmpeg` executable.')
    else:
      return [path] + self.args + ([
          (("--%s" % k) + (("=%s" % v) if v is not None else "")) for k, v in self.kwargs.iteritems()
        ] if self.kwargs else [])

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

    ''' Get ready to spawn the ``FFmpeg`` subprocess, by allocating
        scratch space and indicating that we're starting an exclusive
        session (at least in the scope of the current interpreter) for
        talking to ``FFmpeg``.

        :returns: ``self``, for use in an ``as`` binding as part of a
        ``with`` construct. '''

    if self.__pending__:
      raise RuntimeError("Cannot invoke ``FFmpeg`` concurrently.")

    self._provision_scratchspace()
    self.__pending__ = True  # indicate pending mode
    return self  # set self as final driver

  def __exit__(self, exc_type, exception, exc_info):

    ''' Handle clean exit for failure and success states after using
        the ``FFmpeg`` subprocess in-context.

        :param exc_type: Class (type) of context-disrupting exception.
        :param exception: Value (object) of context-disrupting exception.
        :param exc_info: ``sys.exc_info`` result for context-disrupting exception.

        :raises Exception: Anything that happens during in-context execution.

        :returns: ``True`` if no exception was encountered. ``False`` otherwise,
        which bubbles up *all* exceptions. '''

    if not self.__pending__:
      raise RuntimeError("Out-of-context ``__exit__`` invocation.")

    self._destroy_scratchspace()

    if exception:
      return False  # @TODO(sgammon): exception suppression? cleanup?
    return True

  def __call__(self, *args, **kwargs):

    ''' API touchpoint for executing the current set of queued/pending
        arguments via ``FFmpeg``.

        :param args: Positional arguments to also pass to ``FFmpeg``.
        :param kwargs: Keyword arguments to also pass to ``FFmpeg``.
        :returns: Return code of the underlying ``subprocess`` call. '''

    # map final arguments, if any
    if args or kwargs:
      self._add_argument(*args, **kwargs)

    # stdout and stderr output
    stdout, stderr = self.target.communicate(self.__input__ or None)
    return self.target.returncode

  ## == Property Mappings == ##
  args = property(lambda self: self.__args__)  # args sent to ``FFmpeg``
  kwargs = property(lambda self: self.__kwargs__)  # kwargs sent to ``FFmpeg``
  target = property(lambda self: self._spawn())  # spawn/grab process
  moment = property(lambda self: self.__moment__)  # subject moment
  output = property(lambda self: self.__output__)  # output location
  scratch = property(lambda self: self.__scratch__)  # scratchspace
