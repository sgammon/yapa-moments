# -*- coding: utf-8 -*-

'''

  yapa demo: setup

'''

# stdlib + setuptools
import os, setuptools


# grab requirements
path_prefix, _deps = os.path.dirname(__file__), []
with open(os.path.join(path_prefix, 'requirements.txt')) as requirements:
  map(_deps.append, map(lambda x: x.replace('\n', ''), requirements))


# packages with dependency links
_CUSTOM_PKGS, _CUSTOM_LINKS = zip(*(
  ('protobuf==2.5.1beta', "git+git://github.com/keenlabs/protobuf.git#egg=protobuf-2.5.1beta"),
  ('hamlish_jinja-2.5.1beta', "git+git://github.com/keenlabs/hamlish-jinja.git#egg=hamlish_jinja-2.5.1beta")
))


setuptools.setup(name="moments",
      version="0.1",
      author="Sam Gammon",
      packages=(
        "moments",
        "test_moments",
      ),
      scripts=["moment.py"],
      tests_require=["nose"],
      author_email="sg@samgammon.com",
      description="Prototype package that generates Everalbum 'moments', which are autogenerated video slideshows.",
      dependency_links=list(_CUSTOM_LINKS),
      url="https://github.com/sgammon/yapa-moments",
      install_requires=[i for i in _deps if not i.startswith('git')] + list(_CUSTOM_PKGS)
)
