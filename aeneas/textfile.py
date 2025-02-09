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

* :class:`~aeneas.textfile.TextFile`, representing a text file;
* :class:`~aeneas.textfile.TextFileFormat`, an enumeration of text file formats;
* :class:`~aeneas.textfile.TextFilter`, an abstract class for filtering text;
* :class:`~aeneas.textfile.TextFilterIgnoreRegex`, a regular expression text filter;
* :class:`~aeneas.textfile.TextFilterTransliterate`, a transliteration text filter;
* :class:`~aeneas.textfile.TextFragment`, representing a single text fragment;
* :class:`~aeneas.textfile.TransliterationMap`, a full transliteration map.
"""

import contextlib
import io
import logging
import os.path
import re
import typing

import bs4

from aeneas.idsortingalgorithm import IDSortingAlgorithm
from aeneas.tree import Tree
from aeneas.language import Language
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


def get_soup(buf: typing.IO[bytes], *, parse_only=None) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(buf, "lxml", parse_only=parse_only)


class TextFileFormat:
    """
    Enumeration of the supported formats for text files.
    """

    MPLAIN = "mplain"
    """
    Multilevel version of the ``PLAIN`` format.

    The text file contains fragments on multiple levels:
    paragraphs are separated by (at least) a blank line,
    sentences are on different lines,
    words will be recognized automatically::

        First sentence of Paragraph One.
        Second sentence of Paragraph One.

        First sentence of Paragraph Two.

        First sentence of Paragraph Three.
        Second sentence of Paragraph Three.
        Third sentence of Paragraph Three.

    The above will produce the following text tree::

        Paragraph1 ("First ... One.")
          Sentence1 ("First ... One.")
            Word1 ("First")
            Word2 ("sentence")
            ...
            Word5 ("One.")
          Sentence2 ("Second ... One.")
            Word1 ("Second")
            Word2 ("sentence")
            ...
            Word5 ("One.")
        Paragraph2 ("First ... Two.")
          Sentence1 ("First ... Two.")
            Word1 ("First")
            Word2 ("sentence")
            ...
            Word5 ("Two.")
        ...

    """

    MUNPARSED = "munparsed"
    """
    Multilevel version of the ``UNPARSED`` format.

    The text file contains fragments on three levels:
    level 1 (paragraph), level 2 (sentence), level 3 (word)::

        <?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
         <head>
          <meta charset="utf-8"/>
          <link rel="stylesheet" href="../Styles/style.css" type="text/css"/>
          <title>Sonnet I</title>
         </head>
         <body>
          <div id="divTitle">
           <h1>
            <span id="p000001">
             <span id="p000001s000001">
              <span id="p000001s000001w000001">I</span>
             </span>
            </span>
           </h1>
          </div>
          <div id="divSonnet">
           <p class="stanza" id="p000002">
            <span id="p000002s000001">
             <span id="p000002s000001w000001">From</span>
             <span id="p000002s000001w000002">fairest</span>
             <span id="p000002s000001w000003">creatures</span>
             <span id="p000002s000001w000004">we</span>
             <span id="p000002s000001w000005">desire</span>
             <span id="p000002s000001w000006">increase,</span>
            </span><br/>
            <span id="p000002s000002">
             <span id="p000002s000002w000001">That</span>
             <span id="p000002s000002w000002">thereby</span>
             <span id="p000002s000002w000003">beauty’s</span>
             <span id="p000002s000002w000004">rose</span>
             <span id="p000002s000002w000005">might</span>
             <span id="p000002s000002w000006">never</span>
             <span id="p000002s000002w000007">die,</span>
            </span><br/>
            ...
           </p>
           ...
          </div>
         </body>
        </html>

    """

    PARSED = "parsed"
    """
    The text file contains the fragments,
    one per line, with the syntax ``id|text``,
    where `id` is a non-empty fragment identifier
    and `text` is the text of the fragment::

        f001|Text of the first fragment
        f002|Text of the second fragment
        f003|Text of the third fragment

    """

    PLAIN = "plain"
    """
    The text file contains the fragments,
    one per line, without explicitly-assigned identifiers::

        Text of the first fragment
        Text of the second fragment
        Text of the third fragment

    """

    SUBTITLES = "subtitles"
    """
    The text file contains the fragments,
    each fragment is contained in one or more consecutive lines,
    separated by (at least) a blank line,
    without explicitly-assigned identifiers.
    Use this format if you want to output to SRT/TTML/VTT
    and you want to keep multilines in the output file::

        Fragment on a single row

        Fragment on two rows
        because it is quite long

        Another one liner

        Another fragment
        on two rows

    """

    UNPARSED = "unparsed"
    """
    The text file is a well-formed HTML/XHTML file,
    where the text fragments have already been marked up.

    The text fragments will be extracted by matching
    the ``id`` and/or ``class`` attributes of each elements
    with the provided regular expressions::

        <?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
         <head>
          <meta charset="utf-8"/>
          <link rel="stylesheet" href="../Styles/style.css" type="text/css"/>
          <title>Sonnet I</title>
         </head>
         <body>
          <div id="divTitle">
           <h1><span class="ra" id="f001">I</span></h1>
          </div>
          <div id="divSonnet">
           <p>
            <span class="ra" id="f002">From fairest creatures we desire increase,</span><br/>
            <span class="ra" id="f003">That thereby beauty’s rose might never die,</span><br/>
            <span class="ra" id="f004">But as the riper should by time decease,</span><br/>
            <span class="ra" id="f005">His tender heir might bear his memory:</span><br/>
            <span class="ra" id="f006">But thou contracted to thine own bright eyes,</span><br/>
            <span class="ra" id="f007">Feed’st thy light’s flame with self-substantial fuel,</span><br/>
            <span class="ra" id="f008">Making a famine where abundance lies,</span><br/>
            <span class="ra" id="f009">Thy self thy foe, to thy sweet self too cruel:</span><br/>
            <span class="ra" id="f010">Thou that art now the world’s fresh ornament,</span><br/>
            <span class="ra" id="f011">And only herald to the gaudy spring,</span><br/>
            <span class="ra" id="f012">Within thine own bud buriest thy content,</span><br/>
            <span class="ra" id="f013">And tender churl mak’st waste in niggarding:</span><br/>
            <span class="ra" id="f014">Pity the world, or else this glutton be,</span><br/>
            <span class="ra" id="f015">To eat the world’s due, by the grave and thee.</span>
           </p>
          </div>
         </body>
        </html>

    """

    UNPARSED_IMG = "unparsed_img"
    """
    The text file is a well-formed HTML/XHTML file,
    where the text fragments have already been marked up.

    This is same as the ``unparsed`` format, but additionally the text from
    `<img>` `alt` is extracted.

    The text fragments will be extracted by matching
    the ``id`` and/or ``class`` attributes of each elements
    with the provided regular expressions::

        <?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
         <head>
          <meta charset="utf-8"/>
          <link rel="stylesheet" href="../Styles/style.css" type="text/css"/>
          <title>Sonnet I</title>
         </head>
         <body>
          <div id="divTitle">
           <h1><span class="ra" id="f001">I</span></h1>
          </div>
          <div id="divSonnet">
           <p>
            <span class="ra" id="f002">From fairest creatures we desire increase,</span><br/>
            <span class="ra" id="f003">That thereby beauty’s rose might never die,</span><br/>
            <span class="ra" id="f004">But as the riper should by time decease,</span><br/>
            <span class="ra" id="f005">His tender heir might bear his memory:</span><br/>
            <span class="ra" id="f006">But thou contracted to thine own bright eyes,</span><br/>
            <span class="ra" id="f007">Feed’st thy light’s flame with self-substantial fuel,</span><br/>
            <span class="ra" id="f008">Making a famine where abundance lies,</span><br/>
            <span class="ra" id="f009">Thy self thy foe, to thy sweet self too cruel:</span><br/>
            <span class="ra" id="f010">Thou that art now the world’s fresh ornament,</span><br/>
            <span class="ra" id="f011">And only herald to the gaudy spring,</span><br/>
            <span class="ra" id="f012">Within thine own bud buriest thy content,</span><br/>
            <span class="ra" id="f013">And tender churl mak’st waste in niggarding:</span><br/>
            <span class="ra" id="f014">Pity the world, or else this glutton be,</span><br/>
            <span class="ra" id="f015">To eat the world’s due, by the grave and thee.</span>
           </p>

           <figure>
            <img alt="This is an image description." src="img.png"/>
           </figure>

          </div>
         </body>
        </html>
    """

    MULTILEVEL_VALUES = (MPLAIN, MUNPARSED)
    """ List of all multilevel formats """

    ALLOWED_VALUES = (
        MPLAIN,
        MUNPARSED,
        PARSED,
        PLAIN,
        SUBTITLES,
        UNPARSED,
        UNPARSED_IMG,
    )
    """ List of all the allowed values """


class TextFragment:
    """
    A text fragment.

    Internally, all the text objects are Unicode strings.

    :param string identifier: the identifier of the fragment
    :param language: the language of the text of the fragment
    :type  language: :class:`~aeneas.language.Language`
    :param list lines: the lines in which text is split up
    :param list filtered_lines: the lines in which text is split up,
                                possibly filtered for the alignment purpose
    :raises: TypeError: if ``identifier`` is not a Unicode string
    :raises: TypeError: if ``lines`` is not an instance of ``list`` or
                        it contains an element which is not a Unicode string
    """

    def __init__(
        self,
        identifier: str | None = None,
        language: Language | None = None,
        lines: list[str] | None = None,
        filtered_lines: list[str] | None = None,
    ) -> None:
        self.identifier = identifier
        self.language = language
        self.lines = lines
        self.filtered_lines = filtered_lines

    def __len__(self) -> int:
        if self.lines is None:
            return 0
        return len(self.lines)

    def __str__(self) -> str:
        return f"{self.identifier} {self.text}"

    @property
    def identifier(self) -> str | None:
        """
        The identifier of the text fragment.

        :rtype: string
        """
        return self.__identifier

    @identifier.setter
    def identifier(self, identifier: str | None):
        if identifier is not None and not isinstance(identifier, str):
            raise TypeError("identifier is not a string")
        self.__identifier = identifier

    @property
    def language(self) -> Language | None:
        """
        The language of the text fragment.

        :rtype: :class:`~aeneas.language.Language`
        """
        return self.__language

    @language.setter
    def language(self, language: Language | None):
        # NOTE disabling this check to allow for language codes not listed in Language
        # COMMENTED if (language is not None) and (language not in Language.ALLOWED_VALUES):
        # COMMENTED     raise ValueError(u"language value is not allowed")
        self.__language = language

    @property
    def lines(self) -> list[str] | None:
        """
        The lines of the text fragment.

        :rtype: list of strings
        """
        return self.__lines

    @lines.setter
    def lines(self, lines: list[str] | None):
        if lines is not None:
            if not isinstance(lines, list):
                raise TypeError("lines is not an instance of list")
            for line in lines:
                if not isinstance(line, str):
                    raise TypeError("lines contains an element which is not a string")
        self.__lines = lines

    @property
    def text(self) -> str:
        """
        The text of the text fragment.

        :rtype: string
        """
        if self.lines is None:
            return ""
        return " ".join(self.lines)

    @property
    def characters(self) -> int:
        """
        The number of characters in this text fragment,
        including line separators, if any.

        :rtype: int
        """
        return len(self.text)

    @property
    def chars(self) -> int:
        """
        Return the number of characters of the text fragment,
        not including the line separators.

        :rtype: int
        """
        if self.lines is None:
            return 0
        return sum(len(line) for line in self.lines)

    @property
    def filtered_text(self) -> str:
        """
        The filtered text of the text fragment.

        :rtype: string
        """
        if self.filtered_lines is None:
            return ""
        return " ".join(self.filtered_lines)

    @property
    def filtered_characters(self) -> int:
        """
        The number of filtered characters in this text fragment.

        :rtype: int
        """
        return len(self.filtered_text)


class TextFile:
    """
    A tree of text fragments, representing a text file.

    :param string file_path: the path to the text file.
                             If not ``None`` (and also ``file_format`` is not ``None``),
                             the file will be read immediately.
    :param file_format: the format of the text file
    :type  file_format: :class:`~aeneas.textfile.TextFileFormat`
    :param dict parameters: additional parameters used to parse the text file
    :raises: OSError: if ``file_path`` cannot be read
    :raises: TypeError: if ``parameters`` is not an instance of ``dict``
    :raises: ValueError: if ``file_format`` value is not allowed
    """

    DEFAULT_ID_FORMAT = "f%06d"

    def __init__(
        self,
        file_path: str | None = None,
        file_format: str | None = None,
        parameters: dict | None = None,
    ):
        self.file_path = file_path
        self.file_format = file_format
        self.parameters = {} if parameters is None else parameters
        self.fragments_tree = Tree()
        if self.file_path is not None and self.file_format is not None:
            self._read_from_file()

    def __len__(self):
        return len(self.fragments)

    def __str__(self):
        msg = []
        if self.fragments_tree is not None:
            for node in self.fragments_tree.pre:
                if not node.is_empty:
                    indent = " " * 2 * (node.level - 1)
                    msg.append(f"{indent}{node.value}")
        return "\n".join(msg)

    @property
    def fragments_tree(self):
        """
        Return the current tree of fragments.

        :rtype: :class:`~aeneas.tree.Tree`
        """
        return self.__fragments_tree

    @fragments_tree.setter
    def fragments_tree(self, fragments_tree):
        self.__fragments_tree = fragments_tree

    @property
    def children_not_empty(self):
        """
        Return the direct not empty children of the root of the fragments tree,
        as ``TextFile`` objects.

        :rtype: list of :class:`~aeneas.textfile.TextFile`
        """
        children = []
        for child_node in self.fragments_tree.children_not_empty:
            child_text_file = self.get_subtree(child_node)
            child_text_file.set_language(child_node.value.language)
            children.append(child_text_file)
        return children

    @property
    def file_path(self):
        """
        The path of the text file.

        :rtype: string
        """
        return self.__file_path

    @file_path.setter
    def file_path(self, file_path):
        if file_path is not None and not os.path.isfile(file_path):
            raise OSError(f"Text file {file_path!r} does not exist or is not a file")
        self.__file_path = file_path

    @property
    def file_format(self):
        """
        The format of the text file.

        :rtype: :class:`~aeneas.textfile.TextFileFormat`
        """
        return self.__file_format

    @file_format.setter
    def file_format(self, file_format):
        if file_format is not None and file_format not in TextFileFormat.ALLOWED_VALUES:
            raise ValueError(f"Text file format {file_format!r} is not allowed")
        self.__file_format = file_format

    @property
    def parameters(self):
        """
        Additional parameters used to parse the text file.

        :rtype: dict
        """
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters: dict | None):
        if parameters is not None and not isinstance(parameters, dict):
            raise TypeError("parameters is not an instance of dict")
        self.__parameters = parameters

    @property
    def chars(self) -> int:
        """
        Return the number of characters of the text file,
        not counting line or fragment separators.

        :rtype: int
        """
        return sum(fragment.chars for fragment in self.fragments)

    @property
    def characters(self) -> int:
        """
        The number of characters in this text file.

        :rtype: int
        """
        return sum(f.characters for f in self.fragments)

    @property
    def fragments(self):
        """
        The current list of text fragments
        which are the children of the root node
        of the text file tree.

        :rtype: list of :class:`~aeneas.textfile.TextFragment`
        """
        return self.fragments_tree.vchildren_not_empty

    def add_fragment(self, fragment, as_last: bool = True):
        """
        Add the given text fragment as the first or last child of the root node
        of the text file tree.

        :param fragment: the text fragment to be added
        :type  fragment: :class:`~aeneas.textfile.TextFragment`
        :param bool as_last: if ``True`` append fragment, otherwise prepend it
        """
        if not isinstance(fragment, TextFragment):
            raise TypeError("fragment is not an instance of TextFragment")
        self.fragments_tree.add_child(Tree(value=fragment), as_last=as_last)

    def get_subtree(self, root: Tree):
        """
        Return a new :class:`~aeneas.textfile.TextFile` object,
        rooted at the given node ``root``.

        :param root: the root node
        :type  root: :class:`~aeneas.tree.Tree`
        :rtype: :class:`~aeneas.textfile.TextFile`
        """
        if not isinstance(root, Tree):
            raise TypeError("root is not an instance of Tree")

        new_text_file = TextFile()
        new_text_file.fragments_tree = root
        return new_text_file

    def get_slice(self, start: int | None = None, end: int | None = None):
        """
        Return a new list of text fragments,
        indexed from start (included) to end (excluded).

        :param int start: the start index, included
        :param int end: the end index, excluded
        :rtype: :class:`~aeneas.textfile.TextFile`
        """
        if start is not None:
            start = min(max(0, start), len(self) - 1)
        else:
            start = 0

        if end is not None:
            end = min(max(0, end), len(self))
            end = max(end, start + 1)
        else:
            end = len(self)

        new_text = TextFile()
        for fragment in self.fragments[start:end]:
            new_text.add_fragment(fragment)
        return new_text

    def set_language(self, language):
        """
        Set the given language for all the text fragments.

        :param language: the language of the text fragments
        :type  language: :class:`~aeneas.language.Language`
        """
        logger.debug("Setting language: %r", language)
        for fragment in self.fragments:
            fragment.language = language

    def clear(self):
        """
        Clear the text file, removing all the current fragments.
        """
        logger.debug("Clearing text fragments")
        self.fragments_tree = Tree()

    def read_from_list(self, lines: typing.Sequence[str]):
        """
        Read text fragments from a given list of strings::

            [fragment_1, fragment_2, ..., fragment_n]

        :param list lines: the text fragments
        """
        logger.debug("Reading text fragments from list")
        # TODO: Consider either improving this or removing `read_from_list()`.
        self._read_plain(io.BytesIO(b"\n".join([line.encode() for line in lines])))

    def read_from_list_with_ids(self, lines: typing.Sequence[tuple[str, str]]):
        """
        Read text fragments from a given list of tuples::

            [(id_1, text_1), (id_2, text_2), ..., (id_n, text_n)].

        :param list lines: the list of ``[id, text]`` fragments (see above)
        """
        logger.debug("Reading text fragments from list with IDs")
        self._create_text_fragments(
            (line_id, [line_text]) for line_id, line_text in lines
        )

    def _read_from_file(self):
        """
        Read text fragments from file.
        """
        if self.file_format not in TextFileFormat.ALLOWED_VALUES:
            raise ValueError(f"Text file format {self.file_format!r} is not supported.")

        # clear text fragments
        self.clear()

        # parse the contents
        map_read_function = {
            TextFileFormat.MPLAIN: self._read_mplain,
            TextFileFormat.MUNPARSED: self._read_munparsed,
            TextFileFormat.PARSED: self._read_parsed,
            TextFileFormat.PLAIN: self._read_plain,
            TextFileFormat.SUBTITLES: self._read_subtitles,
            TextFileFormat.UNPARSED: self._read_unparsed,
            TextFileFormat.UNPARSED_IMG: self._read_unparsed_img,
        }

        # read the contents of the file
        logger.debug("Reading contents of file %r", self.file_path)

        with open(self.file_path, mode="rb") as f:
            map_read_function[self.file_format](f)

        # log the number of fragments
        logger.debug("Parsed %d fragments", len(self.fragments))

    def _mplain_word_separator(self):
        """
        Get the word separator to split words in mplain format.

        :rtype: string
        """
        word_separator = gf.safe_get(
            self.parameters, gc.PPN_TASK_IS_TEXT_MPLAIN_WORD_SEPARATOR, " "
        )
        if word_separator is None or word_separator == "space":
            return " "
        elif word_separator == "equal":
            return "="
        elif word_separator == "pipe":
            return "|"
        elif word_separator == "tab":
            return "\u0009"
        return word_separator

    def _read_mplain(self, buf: typing.IO[bytes]):
        """
        Read text fragments from a multilevel format text file.

        :param buf: the bytes file object
        """
        logger.debug("Parsing fragments from subtitles text format")
        word_separator = self._mplain_word_separator()
        logger.debug("Word separator is: %r", word_separator)
        lines = [line.decode().strip() for line in buf.readlines()]
        i = 1
        current = 0
        tree = Tree()
        while current < len(lines):
            line_text = lines[current]
            if line_text:
                sentences = [line_text]
                following = current + 1
                while following < len(lines) and lines[following]:
                    sentences.append(lines[following])
                    following += 1

                # here sentences holds the sentences for this paragraph

                # create paragraph node
                paragraph_identifier = f"p{i:06d}"
                paragraph_lines = [" ".join(sentences)]
                paragraph_fragment = TextFragment(
                    identifier=paragraph_identifier,
                    lines=paragraph_lines,
                    filtered_lines=paragraph_lines,
                )
                paragraph_node = Tree(value=paragraph_fragment)
                tree.add_child(paragraph_node)
                logger.debug("Paragraph %s", paragraph_identifier)

                # create sentences nodes
                for j, s in enumerate(sentences, start=1):
                    sentence_identifier = f"{paragraph_identifier}s{j:06d}"
                    sentence_lines = [s]
                    sentence_fragment = TextFragment(
                        identifier=sentence_identifier,
                        lines=sentence_lines,
                        filtered_lines=sentence_lines,
                    )
                    sentence_node = Tree(value=sentence_fragment)
                    paragraph_node.add_child(sentence_node)
                    logger.debug("Sentence %s", sentence_identifier)

                    # create words nodes
                    for k, w in enumerate(
                        (w for w in s.split(word_separator) if w), start=1
                    ):
                        word_identifier = f"{sentence_identifier}w{k:06d}"
                        word_lines = [w]
                        word_fragment = TextFragment(
                            identifier=word_identifier,
                            lines=word_lines,
                            filtered_lines=word_lines,
                        )
                        word_node = Tree(value=word_fragment)
                        sentence_node.add_child(word_node)
                        logger.debug("Word %s", word_identifier)

                # keep iterating
                current = following
                i += 1
            current += 1

        self.fragments_tree = tree

    def _read_munparsed(self, buf: typing.IO[bytes]):
        """
        Read text fragments from an munparsed format text file.

        :param buf: the bytes file object
        """

        def nodes_at_level(root, level: int):
            """Return a dict with the bs4 filter parameters"""
            LEVEL_TO_REGEX_MAP = [
                None,
                gc.PPN_TASK_IS_TEXT_MUNPARSED_L1_ID_REGEX,
                gc.PPN_TASK_IS_TEXT_MUNPARSED_L2_ID_REGEX,
                gc.PPN_TASK_IS_TEXT_MUNPARSED_L3_ID_REGEX,
            ]
            attribute_name = "id"
            regex_string = self.parameters[LEVEL_TO_REGEX_MAP[level]]
            logger.debug("Regex for %s: %r", attribute_name, regex_string)
            regex = re.compile(rf".*\b{regex_string}\b.*")
            return root.findAll(attrs={attribute_name: regex})

        # TODO better and/or parametric parsing,
        #      for example, removing tags but keeping text, etc.
        logger.debug("Parsing fragments from munparsed text format")
        # transform text in a soup object
        soup = get_soup(buf)
        # extract according to class_regex and id_regex
        logger.debug("Finding L1 elements")
        tree = Tree()
        for l1_node in nodes_at_level(soup, 1):
            has_word = False
            try:
                l1_id = l1_node["id"]
                logger.debug("Found L1 node with ID: %r", l1_id)
                paragraph_node = Tree()
                paragraph_text_parts = []
                for l2_node in nodes_at_level(l1_node, 2):
                    l2_id = l2_node["id"]
                    logger.debug("Found L2 node with ID: %r", l2_id)
                    sentence_node = Tree()
                    paragraph_node.add_child(sentence_node)
                    sentence_text_parts = []
                    for l3_node in nodes_at_level(l2_node, 3):
                        l3_id = l3_node["id"]
                        l3_text = l3_node.text
                        logger.debug("Found L3 node with ID: %r", l3_id)
                        logger.debug("Found L3 node with text: %r", l3_text)
                        word_fragment = TextFragment(
                            identifier=l3_id, lines=[l3_text], filtered_lines=[l3_text]
                        )
                        word_node = Tree(value=word_fragment)
                        sentence_node.add_child(word_node)
                        sentence_text_parts.append(l3_text)
                        has_word = True
                    sentence_text = " ".join(sentence_text_parts)
                    paragraph_text_parts.append(sentence_text)
                    sentence_node.value = TextFragment(
                        identifier=l2_id,
                        lines=[sentence_text],
                        filtered_lines=[sentence_text],
                    )
                    logger.debug("Found L2 node with text: %r", sentence_text)
                if has_word:
                    paragraph_text = " ".join(paragraph_text_parts)
                    paragraph_node.value = TextFragment(
                        identifier=l1_id,
                        lines=[paragraph_text],
                        filtered_lines=[paragraph_text],
                    )
                    tree.add_child(paragraph_node)
                    logger.debug("Found L1 node with text: %r", paragraph_text)
                else:
                    logger.debug("Found L1 node but it has no words, skipping")
            except KeyError as exc:
                logger.warning("KeyError (%s) while parsing a L1 node", exc)

        # append to fragments
        self.fragments_tree = tree

    def _read_subtitles(self, buf: typing.IO[bytes]):
        """
        Read text fragments from a subtitles format text file.

        :param buf: the bytes file object
        :raises: ValueError: if the id regex is not valid
        """
        logger.debug("Parsing fragments from subtitles text format")
        id_format = self._get_id_format()
        lines = [line.decode().strip() for line in buf.readlines()]
        pairs = []
        i = 1
        current = 0
        while current < len(lines):
            line_text = lines[current]
            if line_text:
                fragment_lines = [line_text]
                following = current + 1
                while following < len(lines) and len(lines[following]) > 0:
                    fragment_lines.append(lines[following])
                    following += 1
                identifier = id_format % i
                pairs.append((identifier, fragment_lines))
                current = following
                i += 1
            current += 1
        self._create_text_fragments(pairs)

    def _read_parsed(self, buf: typing.IO[bytes]):
        """
        Read text fragments from a parsed format text file.

        :param buf: the bytes file object
        """
        logger.debug("Parsing fragments from parsed text format")
        pairs = []
        for line in buf.readlines():
            pieces = line.decode().split(gc.PARSED_TEXT_SEPARATOR)
            if len(pieces) != 2:
                continue

            if identifier := pieces[0].strip():
                text = pieces[1].strip()
                pairs.append((identifier, [text]))
        self._create_text_fragments(pairs)

    def _read_plain(self, buf: typing.IO[bytes]):
        """
        Read text fragments from a plain format text file.

        :param buf: the bytes file object
        :raises: ValueError: if the id regex is not valid
        """
        logger.debug("Parsing fragments from plain text format")
        id_format = self._get_id_format()
        self._create_text_fragments(
            (id_format % idx, [line.decode().strip()])
            for idx, line in enumerate(buf.readlines(), start=1)
        )

    @staticmethod
    def _get_node_text(node, *, read_img_alt: bool) -> str:
        if node.text:
            return node.text
        elif read_img_alt and node.name == "img":
            alt = node.attrs.get("alt")
            if alt is not None:
                return alt

        return ""

    def _read_unparsed(self, buf: typing.IO[bytes], *, read_img_alt: bool = False):
        """
        Read text fragments from an unparsed format text file.

        :param buf: the bytes file object
        :param bool read_img_alt: if True, read text from `<img/>` tag `alt` attribute
        """

        def make_soup_strainer() -> bs4.SoupStrainer:
            attributes = {}
            for attribute_name, filter_name in {
                "class": gc.PPN_TASK_IS_TEXT_UNPARSED_CLASS_REGEX,
                "id": gc.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX,
            }.items():
                if filter_name not in self.parameters:
                    continue
                if (regex_string := self.parameters[filter_name]) is not None:
                    logger.debug("Regex for %s: %r", attribute_name, regex_string)
                    attributes[attribute_name] = re.compile(rf".*\b{regex_string}\b.*")

            return bs4.SoupStrainer(**attributes)

        # TODO better and/or parametric parsing,
        #      for example, removing tags but keeping text, etc.
        logger.debug("Parsing fragments from unparsed text format")

        # transform text in a soup object
        soup = get_soup(buf, parse_only=make_soup_strainer())

        # extract according to class_regex and id_regex
        text_from_id = {}
        ids = []
        for node in soup.find_all():
            try:
                f_id = node["id"]
                f_text = self._get_node_text(node, read_img_alt=read_img_alt)

                text_from_id[f_id] = f_text
                ids.append(f_id)
            except KeyError as exc:
                logger.warning("KeyError (%s) while parsing a node", exc)

        # sort by ID as requested
        id_sort = gf.safe_get(
            dictionary=self.parameters,
            key=gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT,
            default_value=IDSortingAlgorithm.UNSORTED,
            can_return_none=False,
        )
        logger.debug("Sorting text fragments using %r", id_sort)
        sorted_ids = IDSortingAlgorithm(id_sort).sort(ids)

        # append to fragments
        self._create_text_fragments((key, [text_from_id[key]]) for key in sorted_ids)

    def _read_unparsed_img(self, buf: typing.IO[bytes]):
        """
        Read text fragments from an unparsed format text file, additionally
        extracting image descriptions.

        :param buf: the bytes file object
        """
        return self._read_unparsed(buf, read_img_alt=True)

    def _get_id_format(self):
        """Return the id regex from the parameters"""
        id_format = gf.safe_get(
            self.parameters,
            gc.PPN_TASK_OS_FILE_ID_REGEX,
            self.DEFAULT_ID_FORMAT,
            can_return_none=False,
        )
        try:
            id_format % 1
        except (TypeError, ValueError) as exc:
            raise ValueError("String %r is not a valid ID format", id_format) from exc
        return id_format

    def _create_text_fragments(self, pairs: typing.Iterable[tuple[str, list[str]]]):
        """
        Create text fragment objects and append them to this list.

        :param list pairs: a list of pairs, each pair being (id, [line_1, ..., line_n])
        """
        logger.debug("Creating TextFragment objects")
        text_filter = self._build_text_filter()
        for identifier, lines in pairs:
            self.add_fragment(
                TextFragment(
                    identifier=identifier,
                    lines=lines,
                    filtered_lines=text_filter.apply_filter(lines),
                )
            )

    def _build_text_filter(self) -> "TextFilter":
        """
        Build a suitable TextFilter object.
        """
        text_filter = TextFilter()
        for key, cls, param_name in [
            (gc.PPN_TASK_IS_TEXT_FILE_IGNORE_REGEX, TextFilterIgnoreRegex, "regex"),
            (
                gc.PPN_TASK_IS_TEXT_FILE_TRANSLITERATE_MAP,
                TextFilterTransliterate,
                "map_file_path",
            ),
        ]:
            cls_name = cls.__name__
            param_value = gf.safe_get(self.parameters, key, None)
            if param_value is not None:
                logger.debug("Creating %s object...", cls_name)
                params = {param_name: param_value}
                try:
                    inner_filter = cls(**params)
                    text_filter.add_filter(inner_filter)
                    logger.debug("Creating %s object... done", cls_name)
                except ValueError:
                    logger.exception(
                        "Creating %s object failed",
                        cls_name,
                    )
        return text_filter


class TextFilter:
    """
    A text filter is a function acting on a list of strings,
    and returning a new list of strings derived from the former
    (with the same number of elements).

    For example, a filter might apply a regex to the input string,
    or it might transliterate its characters.

    Filters can be chained, to the left or to the right.
    """

    SPACES_REGEX = re.compile(r" [ ]+")

    def __init__(self):
        self.filters = []

    def add_filter(self, new_filter: "TextFilter", as_last: bool = True):
        """
        Compose this filter with the given ``new_filter`` filter.

        :param new_filter: the filter to be composed
        :type  new_filter: :class:`~aeneas.textfile.TextFilter`
        :param bool as_last: if ``True``, compose to the right, otherwise to the left
        """
        if as_last:
            self.filters.append(new_filter)
        else:
            self.filters = [new_filter] + self.filters

    def apply_filter(self, strings: list[str]) -> list[str]:
        """
        Apply the text filter filter to the given list of strings.

        :param list strings: the list of input strings
        """
        result = strings
        for filt in self.filters:
            result = filt.apply_filter(result)
        logger.debug("Applying regex: %r => %r", strings, result)
        return result


class TextFilterIgnoreRegex(TextFilter):
    """
    Delete the text matching the given regex.

    Leading/trailing spaces, and repeated spaces are removed.

    :param regex regex: the regular expression to be applied
    :raises: ValueError: if ``regex`` is not a valid regex
    """

    def __init__(self, regex: str):
        try:
            self.regex = re.compile(regex)
        except Exception as exc:
            raise ValueError(
                f"String {regex!r} is not a valid regular expression"
            ) from exc
        super().__init__()

    def apply_filter(self, strings: list[str]) -> list[str]:
        return [self._apply_single(s) for s in strings]

    def _apply_single(self, string: str) -> str:
        """Apply filter to single string"""
        result = self.regex.sub("", string)
        result = self.SPACES_REGEX.sub(" ", result).strip()
        return result


class TextFilterTransliterate(TextFilter):
    """
    Transliterate the text using the given map file.

    Leading/trailing spaces, and repeated spaces are removed.

    :param string map_file_path: the path to a map file
    """

    def __init__(self, map_file_path: str):
        super().__init__()
        self.trans_map = TransliterationMap.from_path(map_file_path)

    def apply_filter(self, strings):
        return [self._apply_single(s) for s in strings]

    def _apply_single(self, string):
        """Apply filter to single string"""
        if string is None:
            return None
        result = self.trans_map.transliterate(string)
        result = self.SPACES_REGEX.sub(" ", result).strip()
        return result


class TransliterationMap:
    """
    A transliteration map is a dictionary that maps Unicode characters
    to their equivalent Unicode characters or strings (character sequences).
    If a character is unmapped, its image is the character itself.
    If a character is mapped to the empty string, it will be deleted.
    Otherwise, a character will be replaced with the associated string.

    For its format, please read the initial comment
    included at the top of the ``transliteration.map`` sample file.
    """

    CODEPOINT_REGEX = re.compile(r"U\+([0-9A-Fa-f]+)")
    DELETE_REGEX = re.compile(r"^([^ ]+)$")
    REPLACE_REGEX = re.compile(r"^([^ ]+) ([^ ]+)$")

    def __init__(self, trans_map: dict[str, str]):
        self.trans_map = trans_map

    @classmethod
    def _process_map_rule(cls, line: str) -> typing.Iterator[tuple[str, str]]:
        """
        Process the line string containing a map rule.
        """
        if result := cls.REPLACE_REGEX.match(line):
            what = cls._process_first_group(result.group(1))
            replacement = cls._process_second_group(result.group(2))
            for char in what:
                yield char, replacement
        elif result := cls.DELETE_REGEX.match(line):
            for char in cls._process_first_group(result.group(1)):
                yield char, ""

    @classmethod
    def from_path(cls, file_path: str):
        trans_map = {}
        with open(file_path, encoding="utf-8") as file_obj:
            for line in file_obj:
                # ignore lines starting with "#" or blank (after stripping)
                if line.startswith("#"):
                    continue

                if line := line.expandtabs(tabsize=1).strip():
                    for char, replacement in cls._process_map_rule(line):
                        trans_map[char] = replacement

        return cls(trans_map)

    @classmethod
    def _process_first_group(cls, group: str) -> str:
        """
        Process the first group of a rule.
        """
        if "-" in group:
            # range
            if len(group.split("-")) == 2:
                arr = group.split("-")
                start = cls._parse_codepoint(arr[0])
                end = cls._parse_codepoint(arr[1])
        else:
            # single char/U+xxxx
            start = cls._parse_codepoint(group)
            end = start
        result = []
        if start > -1 and end >= start:
            for index in range(start, end + 1):
                result.append(chr(index))
        return result

    @classmethod
    def _process_second_group(cls, group: str) -> str:
        """
        Process the second group of a (replace) rule.
        """

        def _replace_codepoint(match: re.Match) -> str:
            """
            Replace the matched Unicode hex code
            with the corresponding unicode character
            """
            result = cls._match_to_int(match)
            if result == -1:
                return ""
            return chr(result)

        result = group
        with contextlib.suppress(Exception):
            result = re.sub(cls.CODEPOINT_REGEX, _replace_codepoint, result)
        return result

    @classmethod
    def _parse_codepoint(cls, string: str) -> int:
        """
        Parse the given string, either a Unicode character or ``U+....``,
        and return the corresponding Unicode code point as int.
        """
        if len(string) > 1:
            match = cls.CODEPOINT_REGEX.match(string)
            return cls._match_to_int(match)
        elif len(string) == 1:
            return cls._chr_to_int(string)
        return -1

    @classmethod
    def _match_to_int(cls, match: re.Match) -> int:
        """
        Convert to int the first group of the match,
        representing the hex number in :data:`aeneas.textfile.TransliterationMap.CODEPOINT_REGEX`
        (e.g., ``12AB`` in ``U+12AB``).
        """
        with contextlib.suppress(Exception):
            return int(match.group(1), 16)

        return -1

    @classmethod
    def _chr_to_int(cls, char: str) -> int:
        """
        Convert to int the given character.
        """
        with contextlib.suppress(Exception):
            return ord(char)

        return -1

    def transliterate(self, string: str) -> str:
        return "".join([self.trans_map.get(char, char) for char in string])
