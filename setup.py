from os.path import dirname, join
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand
from sys import exit

package_name = "thimble"

def read(path):
    with open(join(dirname(__file__), path)) as f:
        return f.read()

import re
version_line = read("{0}/_version.py".format(package_name))
match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]$", version_line, re.M)
version_string = match.group(1)

dependencies = map(str.split, read("requirements.txt").split())

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        exit(tox.cmdline([]))

setup(name=package_name,
      version=version_string,
      description="A Twisted thread-pool based wrapper for blocking APIs.",
      long_description=read("README.rst"),
      url="https://github.com/lvh/{0}".format(package_name),

      author='lvh',
      author_email='_@lvh.io',

      license='Apache 2.0',
      keywords="twisted threads thread compat compatibility async asynchronous",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Framework :: Twisted",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 2 :: Only",
          "Programming Language :: Python :: 2.7",
      ],

      packages=find_packages(),
      install_requires=dependencies,
      test_suite="{0}.test".format(package_name),
      cmdclass={'test': Tox},

      zip_safe=True)
