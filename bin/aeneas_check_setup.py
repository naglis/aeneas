#!/usr/bin/env python

# aeneas is a Python/C library and a set of tools
# to automagically synchronize audio and text (aka forced alignment)
#
# Copyright (C) 2012-2013, Alberto Pettarin (www.albertopettarin.it)
# Copyright (C) 2013-2015, ReadBeyond Srl   (www.readbeyond.it)
# Copyright (C) 2015-2017, Alberto Pettarin (www.albertopettarin.it)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Check whether the setup of aeneas was successful.

Running this script makes sense only
if you git-cloned the original GitHub repository
and/or if you are interested in contributing to the
development of aeneas.
"""

import os
import sys

__author__ = "Alberto Pettarin"
__email__ = "aeneas@readbeyond.it"
__copyright__ = """
    Copyright 2012-2013, Alberto Pettarin (www.albertopettarin.it)
    Copyright 2013-2015, ReadBeyond Srl   (www.readbeyond.it)
    Copyright 2015-2017, Alberto Pettarin (www.albertopettarin.it)
"""
__license__ = "GNU AGPL 3"
__status__ = "Production"
__version__ = "1.7.3"

ANSI_ERROR = "\033[91m"
ANSI_OK = "\033[92m"
ANSI_WARNING = "\033[93m"
ANSI_END = "\033[0m"

IS_POSIX = os.name == "posix"


def print_error(msg):
    """Print an error message"""
    if IS_POSIX:
        print("{}[ERRO] {}{}".format(ANSI_ERROR, msg, ANSI_END))
    else:
        print("[ERRO] %s" % (msg))


def print_info(msg):
    """Print an info message"""
    print("[INFO] %s" % (msg))


def print_success(msg):
    """Print a warning message"""
    if IS_POSIX:
        print("{}[INFO] {}{}".format(ANSI_OK, msg, ANSI_END))
    else:
        print("[INFO] %s" % (msg))


def print_warning(msg):
    """Print a warning message"""
    if IS_POSIX:
        print("{}[WARN] {}{}".format(ANSI_WARNING, msg, ANSI_END))
    else:
        print("[WARN] %s" % (msg))


def check_import():
    """
    Try to import the aeneas package and return ``True`` if that fails.
    """
    try:
        import aeneas

        print_success("aeneas         OK")
        return False
    except ImportError:
        print_error("aeneas         ERROR")
        print_info("  Unable to load the aeneas Python package")
        print_info("  This error is probably caused by:")
        print_info(
            "    A. you did not download/git-clone the aeneas package properly; or"
        )
        print_info("    B. you did not install the required Python packages:")
        print_info("      1. BeautifulSoup4")
        print_info("      2. lxml")
        print_info("      3. numpy")
    except Exception as e:
        print_error(e)
    return True


def main():
    """The entry point for this module"""
    # first, check we can import aeneas package, exiting on failure
    if check_import():
        sys.exit(1)

    # import and run the built-in diagnostics
    from aeneas.diagnostics import Diagnostics

    errors, warnings, c_ext_warnings = Diagnostics.check_all()
    if errors:
        sys.exit(1)
    if c_ext_warnings:
        print_warning(
            "All required dependencies are met but at least one Python C extension is not available"
        )
        print_warning("You can still run aeneas but it will be slower")
        print_warning("Enjoy running aeneas!")
        sys.exit(2)
    else:
        print_success(
            "All required dependencies are met and all available Python C extensions are working"
        )
        print_success("Enjoy running aeneas!")
        sys.exit(0)


if __name__ == "__main__":
    main()
