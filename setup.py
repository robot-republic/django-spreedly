from distutils.core import setup

version = '0.1'

setup(name='django-spreedly',
      version=version,
      description="Spreedly hook-ins for Django, forked from shelfworthy/django-spreedly",
      author="Jon Smelquist",
      author_email="jon.smelquist@gmail.com",
      url="http://github.com/jsmelquist/django-spreedly",
      packages = ['spreedly']
      )
