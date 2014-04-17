# -*- coding: utf-8 -*-

'''

  yapa moments demo: CLI

'''

# stdlib
import sys
import pdb
import logging
import traceback

# local
from . import api

# canteen
from canteen.util import cli


class Moment(cli.Tool):

  ''' Exposes :py:mod:`moments` functionality (from Everalbum)
      via a handy command line interface. '''

  arguments = (
    ('--debug', '-d', {'action': 'store_true', 'help': 'debug mode: drop into PDB on exception'}),
    ('--quiet', '-q', {'action': 'store_true', 'help': 'quiet mode: suppress most output'}),
    ('--verbose', '-v', {'action': 'store_true', 'help': 'verbose mode: be louder about status output'}),
    ('--progress', '-p', {'action': 'store_true', 'help': 'show a bitchin progress bar about stuff'})
  )

  class Create(cli.Tool):

    ''' Allows a user to generate a *moment* from a series of images
        via CLI. '''

    arguments = (
      ('--input', '-i', {'type': str, 'help': 'globbed path of source images'}),
      ('--output', '-o', {'type': str, 'help': 'full path to desired video output location'}),
      ('--audio', '-a', {'type': str, 'help': 'full path to an audio track to attach'}),
      ('--framerate', '-f', {'type': str, 'help': 'input framerate to enforce for reading sources (default: 1)'}),
      ('--bitrate', '-b', {'type': str, 'help': 'desired video bitrate (default: "5000k")'}),
      ('--size', '-s', {'type': int, 'help': 'desired size of the smaller output video dimension (default: 300px)'}),
      ('--loop', '-l', {'action': 'store_true', 'help': 'loop the video until the audio is finished (does nothing with no audio)'}),
      ('--length', '-t', {'type': int, 'help': 'the desired length of the output video'}),
      ('--safe', '-n', {'action': 'store_false', 'help': 'don\'t overwrite existing videos (disabled by default)'})
    )

    def execute(arguments):

      ''' Executes the :py:class:`Moment.Create` flow, which creates an
          *Everalbum* moment video from a set of source images.

          :param arguments: :py:class:`argparse.Arguments` object indicating
          desired arguments, as provided by Canteen's :py:class:`cli.Tool` system.

          :returns: Exits directly with Unix-compliant exit code. '''

      try:
        return sys.exit(1 if not api.Moment(arguments.input, arguments.output, **{
          'audio': arguments.audio or None,
          'debug': arguments.debug or False,
          'quiet': arguments.quiet or False,
          'verbose': arguments.verbose or (arguments.debug or False),
          'framerate': arguments.framerate or '1',
          'bitrate': arguments.bitrate or '5000k',
          'progress': arguments.progress or True,
          'size': arguments.size or 500,
          'loop': arguments.loop or False,
          'length': arguments.length or 60,
          'safe': not (arguments.safe or True)
        })(sys.stdin, sys.stdout, sys.stderr) else 0)

      except Exception:

        if arguments.debug: pdb.set_trace()
        if not arguments.quiet:
          traceback.print_exception(*sys.exc_info())
          logging.critical('Moment tool encountered a fatal error. Exiting.')
        return sys.exit(1)


MomentTool = Moment  # alias to `MomentTool` to preserve "tool name"
