# -*- coding: utf-8 -*-

'''

  yapa moments demo: CLI

'''

# canteen
from canteen.util import cli


class MomentTool(cli.Tool):

  ''' Exposes :py:mod:`moments` functionality (from Everalbum)
      via a handy command line interface. '''

  arguments = (
    ('--debug', '-d', {'action': 'store_true', 'help': 'debug mode: drop into PDB on exception'}),
    ('--quiet', '-q', {'action': 'store_true', 'help': 'quiet mode: suppress most output'}),
    ('--verbose', '-v', {'action': 'store_true', 'help': 'verbose mode: be louder about status output'})
  )

  class Implode(cli.Tool):

    ''' Allows a user to generate a *moment* from a series of images
        via CLI. '''

    arguments = (
      ('--input', '-i', {'type': str, 'help': 'globbed path or comma-separated list of source images'}),
      ('--output', '-o', {'type': str, 'help': 'full path to desired video output location'}),
      ('--audio', '-a', {'type': str, 'help': 'full path to an audio track to attach'})
    )

    def execute(arguments):

      '''  '''

      pass
