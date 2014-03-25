import sys
import os
from setuptools import setup, find_packages

if sys.version < '3.3.0':
    raise Exception('sorry, need Python >= 3.3.0')


setup(name='sfss',
      version = '0.2dev',
      description="Small file storage service",
      author="zhangkaizhao",
      author_email="zhangkaizhao@gmail.com",
      license="BSD",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'aiohttp',
        'aiomemcache',
        ],
      entry_points= {
        'console_scripts': [
            'sfss = sfss.wsgi:main',
            ]
        },
      )
