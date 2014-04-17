# -*- coding: utf-8 -*-

'''

  yapa moments demo: API

'''

# stdlib
import os
import pdb
import glob
import collections

# imaging / NumPy
from PIL import Image


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
  __bitrate__ = None  # base bitrate to use for this video
  __framerate__ = None  # base frame rate to enforce for this video
  __progress__ = None  # bool flag: whether to show a progress bar
  __size__ = None  # desired target size for smallest dimension
  __loop__ = None  # loop the video until audio is done
  __safe__ = None  # whether to overwrite target files
  __length__ = None  # the output video's ending length

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
  bitrate = property(lambda self: self.__bitrate__)
  framerate = property(lambda self: self.__framerate__)
  progress = property(lambda self: self.__progress__)
  size = property(lambda self: self.__size__)
  loop = property(lambda self: self.__loop__)
  safe = property(lambda self: self.__safe__)
  length = property(lambda self: self.__length__)


class Moment(base.MomentBase):

  ''' Class representing an individual ``moment`` (a slideshow video),
      generated from a set of images. Holds references to local ``FFmpeg``
      driver instance and manages options. '''

  __source__ = None  # actual handles to source images (not config, like above)
  __target__ = None  # actual handle to output video (not config, like above)
  __driver__ = None  # driver to `ffmpeg`, which subprocesses when neccessary
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
  def _resize_and_crop(self, img, modified_paths, size, crop_type='middle'):
      """
      Resize and crop an image to fit the specified size.

      args:
          img_path: path for the image to resize.
          modified_path: path to store the modified image.
          size: `(width, height)` tuple.
          crop_type: can be 'top', 'middle' or 'bottom', depending on this
              value, the image will cropped getting the 'top/left', 'middle' or
              'bottom/right' of the image to fit the size.
      raises:
          Exception: if can not open the file in img_path of there is problems
              to save the image.
          ValueError: if an invalid `crop_type` is provided.
      """

      # Get current and desired ratio for the images
      img_ratio = img.size[0] / float(img.size[1])
      ratio = size[0] / float(size[1])
      #The image is scaled/cropped vertically or horizontally depending on the ratio
      if ratio > img_ratio:
          img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))), Image.ANTIALIAS)
          # Crop in the top, middle or bottom
          if crop_type == 'top':
              box = (0, 0, img.size[0], size[1])
          elif crop_type == 'middle':
              box = (0, int(round((img.size[1] - size[1]) / 2)), img.size[0],
                     int(round((img.size[1] + size[1]) / 2)))
          elif crop_type == 'bottom':
              box = (0, img.size[1] - size[1], img.size[0], img.size[1])
          else :
              raise ValueError('ERROR: invalid value for crop_type')
          img = img.crop(box)
      elif ratio < img_ratio:
          img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]),
                  Image.ANTIALIAS)
          # Crop in the top, middle or bottom
          if crop_type == 'top':
              box = (0, 0, size[0], img.size[1])
          elif crop_type == 'middle':
              box = (int(round((img.size[0] - size[0]) / 2)), 0,
                     int(round((img.size[0] + size[0]) / 2)), img.size[1])
          elif crop_type == 'bottom':
              box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
          else :
              raise ValueError('ERROR: invalid value for crop_type')
          img = img.crop(box)
      else:
          img = img.resize((size[0], size[1]), Image.ANTIALIAS)
          # If the scale is the same, we do not need to crop

      for modified_path in ([modified_paths] if not isinstance(modified_paths, (list, tuple)) else modified_paths):
        img.save(modified_path)

  def _validate_input(self, source=None):

    ''' Validates and normalizes input stream of images to be
        created into a new :py:class:`Moment` video. Responsible
        for input image aspect ratio, size and format.

        :param source: Alternate source, to override ``self.options.source``.
        Defaults to ``None``.

        :returns: ``self``, for easy chainability. '''

    # scan globbed matches
    _buffer = []
    for image_i, input_item in enumerate(glob.iglob(source or self.options.source)):
      _buffer.append((image_i, input_item))

    for image_i, input_item in _buffer:

      try:
        os.stat(input_item)
      except:
        if self.options.debug: pdb.set_trace()
        self.logging.critical('Moment tool encountered fatal error scanning input item: "%s".' % input_item)
      else:
        self.logging.info('Found valid source image "%s"...' % input_item)

        # open up image and make sure aspect ratio/format/size is all good
        with open(input_item, 'rb') as target_image:

          # open in PIL
          img = Image.open(target_image)
          img.convert("RGBA")

          # calculate aspect ratio
          width, height = img.size
          ratio = max(float(self.options.size) / width, float(self.options.size) / height)

          if self.options.debug:
            self.logging.debug('... has format %s.' % img.format)
            self.logging.debug('... has width %s.' % width)
            self.logging.debug('... has height %s.' % height)
            self.logging.debug('... has aspect ratio %s.' % ratio)

          try:

            _target_paths = []
            for frame_i in xrange(0, ((self.options.length * int(self.options.framerate)) / len(_buffer))):
              _target_paths.append('.'.join((os.path.join(self.driver.scratch, "frame_%s%s" % (str(image_i).zfill(3), str(frame_i).zfill(3))), 'jpg')))

            self._resize_and_crop(img, _target_paths, (self.options.size, self.options.size))

            if self.options.verbose:
              self.logging.debug('... generated thumbnail of size %s at:' % str((self.options.size, self.options.size)))
              for i in _target_paths:
                self.logging.debug('........ %s' % i)

          except:
            self.logging.error('Encountered error resizing image "%s" to size %s.' % (input_item, str((self.options.size, self.options.size))))
            raise

          else:
            # saving succeeded - add to our set of source images
            self.__source__.append(input_item)

    return self

  def _validate_output(self, target=None):

    ''' Validate that we can properly write to the specified
        output location at ``target``. Usually dispatched as
        part of the CLI flow.

        :param target: Alternate target, to override ``self.options.target``.
        Defaults to ``None``.

        :returns: ``self``, for easy chainability. '''

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

    ''' Call override that provides an interface for CLI or API-based
        callers to optionally override ``std{in,out,err}``. This is
        where ``ffmpeg`` is actually dispatched.

        :param stdin: Override for standard in.
        :param stdout: Override for standard out.
        :param stderr: Override for standard error.

        :returns: Boolean flag (``True`` or ``False``) indicating success
        or failure. Usually translated to an exit code for Unix when used
        with the CLI. '''

    # map file descriptors
    self.__stdin__, self.__stdout__, self.__stderr__ = (
      stdin, stdout, stderr
    )

    # acquire driver and start working
    with self.driver as ffmpeg:

      # check input and gather files
      if self._validate_input() and self._validate_output():
        self.logging.info('Creating new Moment from %s input images...' % len(self.source))

        filters = ",".join([  # video filters (watermark, then base filters)
          "movie=resources/watermark.png [watermark]; [in][watermark] overlay=main_w-overlay_w-10:main_h-overlay_h-10 [out]"
        ])

        # calculate target glob and audio
        target_glob = os.path.join(self.driver.scratch, "frame_*.jpg")
        audio = [] if not self.options.audio else [i for i in [
          "-i",
          self.options.audio,
          "-b:a",
          "192k",
          "-c:a",
          "aac",
          "-strict",
          "-2",
          "-b:a",
          "64k",
          "-loop" if self.options.loop else None,
          "1" if self.options.loop else None
        ] if i is not None]

        ffargs = [

          "-r",                                     # input rate
          "%s" % self.options.framerate,            # == framerate
          "-pattern_type",                          # set pattern type
          "glob",                                   # == glob
          "-i",                                     # input flag
          '%s' % target_glob,                       # == input glob
          ] + audio + [
          "-c:v",                                   # ??? (maybe 'create video?')
          "libx264",                                # output muxer
          "-vf",                                    # add video filter
          filters,                                  # == filter for FPS rate and chroma
          "-pix_fmt",                               # picture format
          "yuv420p",                                # == currently JPEG
          "-b:v",                                   # video bitrate
          "%s" % self.options.bitrate,              # == bitrate
          "-y" if not self.options.safe else "-n",  # overwrite output or not
          "-t",                                     # output time
          "%s" % self.options.length,               # output video length
          self.target                               # output video location

        ]

        ffmpeg(*ffargs)  # execute! :)

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
