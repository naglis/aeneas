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

import importlib.util
import unittest

import numpy

from .common import BaseCase


@unittest.skipIf(
    importlib.util.find_spec("aeneas.cdtw.cdtw") is None,
    "CDTW C extension is not available",
)
class TestCDTW(BaseCase):
    MFCC1 = "res/cdtw/mfcc1_12_1332"
    MFCC2 = "res/cdtw/mfcc2_12_868"

    def test_compute_path(self):
        import aeneas.cdtw.cdtw as cdtw

        mfcc1 = numpy.loadtxt(self.file_path(self.MFCC1))
        mfcc2 = numpy.loadtxt(self.file_path(self.MFCC2))
        _, n = mfcc1.shape
        _, m = mfcc2.shape
        delta = 3000
        if delta > m:
            delta = m

        best_path = cdtw.compute_best_path(mfcc1, mfcc2, delta)

        self.assertEqual(len(best_path), 1418)
        self.assertEqual(best_path[0], (0, 0))
        self.assertEqual(best_path[-1], (n - 1, m - 1))
