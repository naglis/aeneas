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
A generic rooted, ordered, levelled tree.

.. versionadded:: 1.5.0
"""

import copy
import logging
import typing

import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class Tree:
    """
    A generic rooted, ordered, levelled tree.

    Nodes can contain arbitrary (possibly, different) types of data.

    The children of a node are stored in the same order
    as they are inserted.

    The node keeps some extra information (parent node, level)
    which is useful when building or visiting a full tree.

    Two visits are implemented: depth-first and level-order,
    with the possibility of returning only the leaves.

    This class is optimized for ease of use
    with :class:`~aeneas.textfile.TextFragment` and
    :class:`~aeneas.syncmap.SyncMapFragment` objects,
    not for best performance or minimum memory footprint.
    Using this class should be fine for representing
    any reasonable text tree.
    """

    def __init__(self, value=None):
        self.value = value
        self.__children = []
        self.__parent = None
        self.__level = 0

    def __str__(self):
        return (
            f"{self.value} (l: {gf.safe_int(self.level)}, c: {gf.safe_int(len(self))})"
        )

    def __len__(self):
        return len(self.children)

    def clone(self) -> "Tree":
        """
        Return a deep copy of this node
        and of any children it might have.

        .. versionadded:: 1.7.0
        """
        return copy.deepcopy(self)

    @property
    def value(self):
        """
        The value stored in this node.

        :rtype: variant
        """
        return self.__value

    @value.setter
    def value(self, value):
        """
        Set the value stored in this node.

        :param variant value: the value/object to be stored
        """
        self.__value = value

    @property
    def children(self) -> list["Tree"]:
        """
        Return the list of the direct children of this node.
        """
        return self.__children

    @property
    def vchildren(self) -> list:
        """
        Return the list of values of the direct children of this node.
        """
        return [n.value for n in self.children]

    @property
    def children_not_empty(self) -> list["Tree"]:
        """
        Return the list of the not empty direct children of this node.
        """
        return [n for n in self.children if not n.is_empty]

    @property
    def vchildren_not_empty(self) -> list["Tree"]:
        """
        Return the list of values of the not empty direct children of this node.
        """
        return [n.value for n in self.children_not_empty]

    @property
    def is_leaf(self) -> bool:
        """
        Return ``True`` if this node is a leaf node.
        """
        return len(self.children) == 0

    @property
    def is_empty(self) -> bool:
        """
        Return ``True`` if this node is empty, i.e., it has no value.
        """
        return self.value is None

    @property
    def parent(self) -> typing.Union["Tree", None]:
        """
        Return the parent node of this node, or ``None`` if this node is a root.
        """
        return self.__parent

    @parent.setter
    def parent(self, parent: "Tree"):
        """
        Set the parent of this node.

        :param parent: the parent node
        :type  parent: :class:`~aeneas.tree.Tree`
        """
        self.__parent = parent

    @property
    def is_root(self) -> bool:
        """
        Return ``True`` if this node is the root node.
        """
        return self.__parent is None

    @property
    def level(self) -> int:
        """
        Return the level of this node,
        starting from ``0`` for the root,
        ``1`` for the direct children of the root,
        and so on.
        """
        return self.__level

    @property
    def is_pleasant(self) -> bool:
        """
        Return ``True`` if all the leaves
        in the subtree rooted at this node
        are at the same level.
        """
        levels = sorted(n.level for n in self.leaves)
        return levels[0] == levels[-1]

    def add_child(self, node: "Tree", as_last: bool = True):
        """
        Add the given child to the current list of children.

        The new child is appended as the last child if ``as_last``
        is ``True``, or as the first child if ``as_last`` is ``False``.

        This call updates the ``__parent`` and ``__level`` fields of ``node``.

        :param node: the child node to be added
        :type  node: :class:`~aeneas.tree.Tree`
        :param bool as_last: if ``True``, append the node as the last child;
                             if ``False``, append the node as the first child
        :raises: TypeError if ``node`` is not an instance of :class:`~aeneas.tree.Tree`
        """
        if not isinstance(node, Tree):
            raise TypeError("node is not an instance of Tree")
        if as_last:
            self.__children.append(node)
        else:
            self.__children = [node] + self.__children
        node.__parent = self
        new_height = 1 + self.level
        for n in node.subtree:
            n.__level += new_height

    def remove_child(self, index: int):
        """
        Remove the child at the given index
        from the current list of children.

        :param int index: the index of the child to be removed
        """
        if index < 0:
            index = index + len(self)
        self.__children = self.__children[0:index] + self.__children[(index + 1) :]

    def remove(self):
        """
        Remove this node from the list of children of its current parent,
        if the current parent is not ``None``, otherwise do nothing.

        .. versionadded:: 1.7.0
        """
        if self.parent is not None:
            for i, child in enumerate(self.parent.children):
                if id(child) == id(self):
                    self.parent.remove_child(i)
                    self.parent = None
                    break

    def remove_children(self, reset_parent: bool = True):
        """
        Remove all the children of this node.

        :param bool reset_parent: if ``True``, set to ``None`` the parent attribute
                                  of the children
        """
        if reset_parent:
            for child in self.children:
                child.parent = None
        self.__children = []

    def get_child(self, index):
        """
        Return the child at the given index
        in the current list of children.

        :param int index: the index of the child to be returned
        """
        return self.children[index]

    def get_vchild(self, index):
        """
        Return the value of the child at the given index
        in the current list of children.

        :param int index: the index of the child to be returned
        """
        return self.get_child(index).value

    @property
    def subtree(self) -> list["Tree"]:
        """
        Return the list of the nodes in the tree rooted at this node, in DFS order.

        Note that this node is always the first element of the returned list.
        If you want to exclude it, use ``node.subtree[1:]``.
        """
        return list(self.dfs)

    @property
    def leaves(self) -> list["Tree"]:
        """
        Return the list of leaves
        in the tree rooted at this node,
        in DFS order.
        """
        return [n for n in self.dfs if n.is_leaf]

    @property
    def vleaves(self):
        """
        Return the list of leaf values
        in the tree rooted at this node,
        in DFS order.

        :rtype: list of variant
        """
        return [n.value for n in self.leaves]

    @property
    def leaves_not_empty(self) -> list["Tree"]:
        """
        Return the list of leaves not empty
        in the tree rooted at this node,
        in DFS order.
        """
        return [n for n in self.dfs if ((n.is_leaf) and (not n.is_empty))]

    @property
    def vleaves_not_empty(self):
        """
        Return the list of not empty leaf values
        in the tree rooted at this node,
        in DFS order.

        :rtype: list of variant
        """
        return [n.value for n in self.leaves_not_empty]

    @property
    def height(self) -> int:
        """
        Return the height of the tree
        rooted at this node,
        that is, the difference between the level
        of a deepest leaf and the level of this node.
        Return ``1`` for a single-node tree,
        ``2`` for a two-levels tree, etc.
        """
        return max(n.level for n in self.subtree) - self.level + 1

    @property
    def dfs(self) -> typing.Iterator["Tree"]:
        """
        Depth-first search of the tree rooted at this node.
        (First visit children, then visit current node.)
        """
        for node in self.children:
            yield from node.dfs
        yield self

    @property
    def pre(self) -> typing.Iterator["Tree"]:
        """
        Pre-order search of the tree rooted at this node.
        (First visit current node, then visit children.)
        """
        yield self
        for node in self.children:
            yield from node.pre

    @property
    def levels(self):
        """
        Return a list of lists of nodes.
        The outer list is indexed by the level.
        Each inner list contains the nodes at that level,
        in DFS order.

        :rtype: list of lists of :class:`~aeneas.tree.Tree`
        """
        ret = [[] for i in range(self.height)]
        for node in self.subtree:
            ret[node.level - self.level].append(node)
        return ret

    @property
    def vlevels(self):
        """
        Return a list of lists of node values.
        The outer list is indexed by the level.
        Each inner list contains the values of the nodes at that level,
        in DFS order.

        Note that values might be ``None``.

        :rtype: list of lists of variant
        """
        return [[n.value for n in level] for level in self.levels]

    def level_at_index(self, index):
        """
        Return the list of nodes at level ``index``,
        in DFS order.

        :param int index: the index
        :rtype: list of :class:`~aeneas.tree.Tree`

        :raises: ValueError if the given ``index`` is not valid
        """
        if not isinstance(index, int):
            raise TypeError("Index is not an integer")
        levels = self.levels
        if index < 0 or index >= len(levels):
            raise ValueError(f"The given level index '{index}' is not valid")
        return self.levels[index]

    def vlevel_at_index(self, index):
        """
        Return the list of node values at level ``index``,
        in DFS order.

        :param int index: the index
        :rtype: list of :class:`~aeneas.tree.Tree`

        :raises: ValueError if the given ``index`` is not valid
        """
        return [n.value for n in self.level_at_index(index)]

    def ancestor(self, index):
        """
        Return the ``index``-th ancestor.

        The 0-th ancestor is the node itself,
        the 1-th ancestor is its parent node,
        etc.

        :param int index: the number of levels to go up
        :rtype: :class:`~aeneas.tree.Tree`
        :raises: TypeError if ``index`` is not an int
        :raises: ValueError if ``index`` is negative
        """
        if not isinstance(index, int):
            raise TypeError("index is not an integer")
        if index < 0:
            raise ValueError("index cannot be negative")
        parent_node = self
        for i in range(index):
            if parent_node is None:
                break
            parent_node = parent_node.parent
        return parent_node

    def keep_levels(self, level_indices):
        """
        Rearrange the tree rooted at this node
        to keep only the given levels.

        The returned Tree will still be rooted
        at the current node, i.e. this function
        implicitly adds ``0`` to ``level_indices``.

        If ``level_indices`` is an empty list,
        only this node will be returned, with no children.

        Elements of ``level_indices`` that do not
        represent valid level indices (e.g., negative, or too large)
        will be ignored and no error will be raised.

        Important: this function modifies
        the original tree in place!

        :param list level_indices: the list of int, representing the levels to keep
        :raises: TypeError if ``level_indices`` is not a list or if
                 it contains an element which is not an int
        """
        if not isinstance(level_indices, list):
            raise TypeError("level_indices is not an instance of list")
        for level in level_indices:
            if not isinstance(level, int):
                raise TypeError("level_indices contains an element not int")
        prev_levels = self.levels
        level_indices = set(level_indices)
        if 0 not in level_indices:
            level_indices.add(0)
        level_indices = level_indices & set(range(self.height))
        level_indices = sorted(level_indices)[::-1]
        # first, remove children
        for level in level_indices:
            for node in prev_levels[level]:
                node.remove_children(reset_parent=False)
        # then, connect to the right new parent
        for i in range(len(level_indices) - 1):
            level = level_indices[i]
            for node in prev_levels[level]:
                parent_node = node.ancestor(level - level_indices[i + 1])
                parent_node.add_child(node)
