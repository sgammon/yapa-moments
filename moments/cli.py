# -*- coding: utf-8 -*-

'''

  yapa moments demo: CLI

'''

# stdlib
import sys
import logging
import traceback

# local
from . import base, api

# canteen
from canteen.util import cli


class Moment(cli.Tool):

  ''' Exposes :py:mod:`moments` functionality (from Everalbum)
      via a handy command line interface. '''

  arguments = (
    ('--debug', '-d', {'action': 'store_true', 'help': 'debug mode: drop into PDB on exception'}),
    ('--quiet', '-q', {'action': 'store_true', 'help': 'quiet mode: suppress most output'}),
    ('--verbose', '-v', {'action': 'store_true', 'help': 'verbose mode: be louder about status output'})
  )

  class Create(cli.Tool):

    ''' Allows a user to generate a *moment* from a series of images
        via CLI. '''

    arguments = (
      ('--input', '-i', {'type': str, 'help': 'globbed path of source images'}),
      ('--output', '-o', {'type': str, 'help': 'full path to desired video output location'}),
      ('--audio', '-a', {'type': str, 'help': 'full path to an audio track to attach'})
    )

    def execute(arguments):

      '''  '''

      try:
        return sys.exit(1 if not api.Moment(arguments.input, arguments.output, **{
          'audio': arguments.audio,
          'debug': arguments.debug,
          'quiet': arguments.quiet,
          'verbose': arguments.verbose
        })(sys.stdin, sys.stdout, sys.stderr) else 0)

      except Exception:

        traceback.print_exception(*sys.exc_info())
        if arguments.debug:
          import pdb; pdb.set_trace()

        logging.critical('Moment tool encountered a fatal error. Exiting.')
        return 1


MomentTool = Moment  # alias to `MomentTool` to preserve "tool name"
