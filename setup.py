from distutils.core import setup
from spreedly import __version__ as version

setup(name='django-spreedly',
      version=version,
      description="Spreedly hook-ins for Django, forked from shelfworthy/django-spreedly",
      author="Jon Smelquist",
      author_email="jon.smelquist@gmail.com",
      url="http://github.com/jsmelquist/django-spreedly",
      packages = ['spreedly','spreedly.pyspreedly']
      )
