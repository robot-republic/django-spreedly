from distutils.core import setup
from spreedly import __version__ as version

setup(name='django-spreedly',
      version=version,
      description="Spreedly hook-ins for Django, forked from shelfworthy/django-spreedly and jsmelquist/django-spreedly",
      author="Jon Smelquist, Kyle Fox",
      author_email="hello@myfotojournal.com",
      url="https://github.com/robot-republic/django-spreedly",
      packages=['spreedly', 'spreedly.pyspreedly']
)
