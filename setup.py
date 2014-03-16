import os
from setuptools import setup, find_packages

setup(name='sfss',
      version = '0.1dev',
      description="Small file storage service",
      author="zhangkaizhao",
      author_email="zhangkaizhao@gmail.com",
      license="BSD",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'morepath',
        'python-memcached',
        ],
      entry_points= {
        'console_scripts': [
            'sfss = sfss.main:main',
            ]
        },
      )
