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

import unittest

from aeneas.idsortingalgorithm import IDSortingAlgorithm


class TestIDSortingAlgorithm(unittest.TestCase):

    IDS = ["b001", "c03", "d4", "a2"]

    def test_invalid_algorithm(self):
        with self.assertRaises(ValueError):
            IDSortingAlgorithm("foo")

    def test_unsorted(self):
        expected = ["b001", "c03", "d4", "a2"]
        idsa = IDSortingAlgorithm(IDSortingAlgorithm.UNSORTED)
        sids = idsa.sort(self.IDS)
        self.assertTrue(sids == expected)

    def test_lexicographic(self):
        expected = ["a2", "b001", "c03", "d4"]
        idsa = IDSortingAlgorithm(IDSortingAlgorithm.LEXICOGRAPHIC)
        sids = idsa.sort(self.IDS)
        self.assertTrue(sids == expected)

    def test_numeric(self):
        expected = ["b001", "a2", "c03", "d4"]
        idsa = IDSortingAlgorithm(IDSortingAlgorithm.NUMERIC)
        sids = idsa.sort(self.IDS)
        self.assertTrue(sids == expected)

    def test_numeric_exception(self):
        bad_ids = ["b002", "d", "c", "a1"]
        idsa = IDSortingAlgorithm(IDSortingAlgorithm.NUMERIC)
        sids = idsa.sort(bad_ids)
        self.assertTrue(sids == bad_ids)


if __name__ == "__main__":
    unittest.main()
