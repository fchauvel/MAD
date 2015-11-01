#!/usr/bin/env python

#
# This file is part of MAD.
#
# MAD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MAD.  If not, see <http://www.gnu.org/licenses/>.
#

import mad

from setuptools import setup, find_packages

setup(name='MAD',
     version=mad.__version__,
     description='Simulations of microservices architectures dynamics',
     author='Franck Chauvel',
     author_email='franck.chauvel@gmail.com',
     license="GPLv3",
     url='https://github.com/fchauvel/MAD',
     download_url="https://github.com/fchauvel/mad/tarball/v"+mad.__version__,
     packages=find_packages(exclude='tests'),
     test_suite = "tests",
     classifiers = [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Science/Research",
                    "Environment :: Console",
                    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                    "Natural Language :: English",
                    "Programming Language :: Python :: 3.2",
                    "Programming Language :: Python :: 3.3",
                    "Programming Language :: Python :: 3.4"
                    ]
     )

