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
This module contains the following classes:

* :class:`~aeneas.idsortingalgorithm.IDSortingAlgorithm`,
  enumerating and implementing the available algorithms to sort
  a list of XML ``id`` attributes.

.. warning:: This module is likely to be refactored in a future version
"""

import logging
import re

logger = logging.getLogger(__name__)


class IDSortingAlgorithm:
    """
    Enumeration of the available algorithms to sort
    a list of XML ``id`` attributes.

    :param algorithm: the id sorting algorithm to be used
    :type  algorithm: :class:`~aeneas.idsortingalgorithm.IDSortingAlgorithm`
    :raises: ValueError: if the value of ``algorithm`` is not allowed
    """

    LEXICOGRAPHIC = "lexicographic"
    """ Lexicographic sorting
    (e.g., ``f020`` before ``f10`` before ``f2``) """

    NUMERIC = "numeric"
    """ Numeric sorting, ignoring any non-digit characters or leading zeroes
    (e.g., ``f2`` (= ``2``) before ``f10`` (= ``10``) before ``f020`` (= ``20``)) """

    UNSORTED = "unsorted"
    """ Do not sort and return the list of identifiers, in their original order
    (e.g., ``f2`` before ``f020`` before ``f10``,
    assuming this was their order in the XML DOM) """

    ALLOWED_VALUES = (LEXICOGRAPHIC, NUMERIC, UNSORTED)
    """ List of all the allowed values """

    def __init__(self, algorithm: str):
        if algorithm not in self.ALLOWED_VALUES:
            raise ValueError("Algorithm value not allowed")
        self.algorithm = algorithm

    def sort(self, ids: list[str]) -> list[str]:
        """
        Sort the given list of identifiers,
        returning a new (sorted) list.

        :param list ids: the list of identifiers to be sorted
        :rtype: list
        """

        def extract_int(string: str) -> int:
            """
            Extract an integer from the given string.

            :param string string: the identifier string
            :rtype: int
            """
            return int(re.sub(r"[^0-9]", "", string))

        tmp = list(ids)
        if self.algorithm == IDSortingAlgorithm.UNSORTED:
            logger.debug("Sorting using UNSORTED")
        elif self.algorithm == IDSortingAlgorithm.LEXICOGRAPHIC:
            logger.debug("Sorting using LEXICOGRAPHIC")
            tmp = sorted(ids)
        elif self.algorithm == IDSortingAlgorithm.NUMERIC:
            logger.debug("Sorting using NUMERIC")
            tmp = ids
            try:
                tmp = sorted(tmp, key=extract_int)
            except (ValueError, TypeError):
                logger.exception(
                    "Not all id values contain a numeric part. Returning the id list unchanged.",
                )
        return tmp
