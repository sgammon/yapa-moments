# -*- coding: utf-8 -*-

'''

  yapa moments demo: base class

'''

# stdlib
import logging


## Globals
_CONFIG = None  # global config
_LOGGER = logging  # global logger


def _set_config(cfg):

  ''' Utility method to set global configuration during
      stateless runs like CLI. '''

  global _CONFIG
  _CONFIG = cfg
  return cfg


class MomentBase(object):

  ''' Packages internal functionality according to a bound
      target object/class. '''

  __config__ = None  # global configuration
  __target__ = None  # target object or class

  def __init__(self, target, config):

    ''' Initialize a new :py:class:`MomentBase` wrapper
        with runtime configuration. '''

    self.__target__, self.__config__ = (
      target, config
    )

  @property
  def config(self):

    ''' Provide current configuration state, as dictated
        by API params or arguments (if using CLI). '''

    return self.__config__ or _CONFIG

  @property
  def logging(self):

    ''' Provide access to a tailored :py:class:`logging.Logger`,
        customized for the callee. '''

    return _LOGGER  # @TODO(sgammon): allow customization
