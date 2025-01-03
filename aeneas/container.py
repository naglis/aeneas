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
This module contains the following classes:

* :class:`~aeneas.container.Container`
  is the main class, exposing functions
  like extracting all entries,
  extracting just one entry,
  listing the entries in the container, etc.;
* :class:`~aeneas.container.ContainerFormat`
  is an enumeration of the supported container formats.
"""

import os
import enum
import tarfile
import zipfile
import sys

from aeneas.logger import Loggable
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf


@enum.unique
class ContainerFormat(enum.Enum):
    """
    Enumeration of the supported container formats.
    """

    EPUB = "epub"
    """ EPUB container """

    TAR = "tar"
    """ TAR container (without compression) """

    TAR_GZ = "tar.gz"
    """ TAR container with GZ compression"""

    TAR_BZ2 = "tar.bz2"
    """ TAR container with BZ2 compression """

    UNPACKED = "unpacked"
    """ Unpacked container (i.e., a directory) """

    ZIP = "zip"
    """ ZIP container """


class Container(Loggable):
    """
    An abstraction for different archive formats like ZIP or TAR,
    exposing common functions like extracting all entries or
    just a single entry, listing the entries, etc.

    An (uncompressed) directory can be used in lieu of a compressed file.

    :param string file_path: the path to the container file (or directory)
    :param container_format: the format of the container
    :type  container_format: :class:`~aeneas.container.ContainerFormat`
    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :param logger: the logger object
    :type  logger: :class:`~aeneas.logger.Logger`
    :raises: TypeError: if ``file_path`` is ``None``
    :raises: ValueError: if ``container_format`` is not ``None`` and is not an allowed value
    """

    TAG = "Container"

    def __init__(
        self,
        file_path: str,
        container_format: ContainerFormat | None = None,
        rconf=None,
        logger=None,
    ):
        if file_path is None:
            raise TypeError("File path is None")
        if container_format is not None and not isinstance(
            container_format, ContainerFormat
        ):
            raise ValueError("Container format not allowed")
        super().__init__(rconf=rconf, logger=logger)
        self.file_path = file_path
        self.container_format = container_format
        self.actual_container = None
        self._set_actual_container()

    @property
    def file_path(self) -> str:
        """
        The path of this container.
        """
        return self.__file_path

    @file_path.setter
    def file_path(self, file_path: str):
        self.__file_path = file_path

    @property
    def container_format(self) -> ContainerFormat | None:
        """
        The format of this container.

        :rtype: :class:`~aeneas.container.ContainerFormat`
        """
        return self.__container_format

    @container_format.setter
    def container_format(self, container_format: ContainerFormat | None):
        self.__container_format = container_format

    @property
    def has_config_xml(self) -> bool:
        """
        Return ``True`` if there is an XML config file in this container,
        ``False`` otherwise.

        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        return self.entry_config_xml is not None

    @property
    def entry_config_xml(self):
        """
        Return the entry (path inside the container)
        of the XML config file in this container,
        or ``None`` if not present.

        :rtype: string
        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        return self.find_entry(gc.CONFIG_XML_FILE_NAME, exact=False)

    @property
    def has_config_txt(self) -> bool:
        """
        Return ``True`` if there is a TXT config file in this container,
        ``False`` otherwise.

        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        return self.entry_config_txt is not None

    @property
    def entry_config_txt(self):
        """
        Return the entry (path inside the container)
        of the TXT config file in this container,
        or ``None`` if not present.

        :rtype: string
        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        return self.find_entry(gc.CONFIG_TXT_FILE_NAME, exact=False)

    @property
    def is_safe(self) -> bool:
        """
        Return ``True`` if the container can be safely extracted,
        that is, if all its entries are safe, ``False`` otherwise.

        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        self.log("Checking if this container is safe")
        for entry in self.entries:
            if not self.is_entry_safe(entry):
                self.log(["This container is not safe: found unsafe entry '%s'", entry])
                return False
        self.log("This container is safe")
        return True

    def is_entry_safe(self, entry) -> bool:
        """
        Return ``True`` if ``entry`` can be safely extracted,
        that is, if it does start with ``/`` or ``../``
        after path normalization, ``False`` otherwise.
        """
        normalized = os.path.normpath(entry)
        if normalized.startswith(os.sep) or normalized.startswith(".." + os.sep):
            self.log(["Entry '%s' is not safe", entry])
            return False
        self.log(["Entry '%s' is safe", entry])
        return True

    @property
    def entries(self):
        """
        Return the sorted list of entries in this container,
        each represented by its full path inside the container.

        :rtype: list of strings (path)
        :raises: TypeError: if this container does not exist
        :raises: OSError: if an error occurred reading the given container
                          (e.g., empty file, damaged file, etc.)
        """
        self.log("Getting entries")
        if not self.exists():
            self.log_exc(
                "This container does not exist. Wrong path?", None, True, TypeError
            )
        if self.actual_container is None:
            self.log_exc(
                "The actual container object has not been set", None, True, TypeError
            )
        return self.actual_container.entries

    def find_entry(self, entry: str, exact: bool = True) -> str | None:
        """
        Return the full path to the first entry whose file name equals
        the given ``entry`` path.

        Return ``None`` if the entry cannot be found.

        If ``exact`` is ``True``, the path must be exact,
        otherwise the comparison is done only on the file name.

        Example: ::

            entry = "config.txt"

        matches: ::

            config.txt            (if exact == True or exact == False)
            foo/config.txt        (if exact == False)
            foo/bar/config.txt    (if exact == False)

        :param string entry: the entry name to be searched for
        :param bool exact: look for the exact entry path
        :rtype: string
        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        if exact:
            self.log(["Finding entry '%s' with exact=True", entry])
            if entry in self.entries:
                self.log(["Found entry '%s'", entry])
                return entry
        else:
            self.log(["Finding entry '%s' with exact=False", entry])
            for ent in self.entries:
                if os.path.basename(ent) == entry:
                    self.log(["Found entry '%s'", ent])
                    return ent
        self.log(["Entry '%s' not found", entry])
        return None

    def read_entry(self, entry: str) -> bytes | None:
        """
        Read the contents of an entry in this container,
        and return them as a byte string.

        Return ``None`` if the entry is not safe
        or it cannot be found.

        :raises: same as :func:`~aeneas.container.Container.entries`
        """
        if not self.is_entry_safe(entry):
            self.log(["Accessing entry '%s' is not safe", entry])
            return None

        if entry not in self.entries:
            self.log(["Entry '%s' not found in this container", entry])
            return None

        self.log(["Reading contents of entry '%s'", entry])
        try:
            return self.actual_container.read_entry(entry)
        except Exception:
            self.log(["An error occurred while reading the contents of '%s'", entry])
            return None

    def decompress(self, output_path: str):
        """
        Decompress the entire container into the given directory.

        :param string output_path: path of the destination directory
        :raises: TypeError: if this container does not exist
        :raises: ValueError: if this container contains unsafe entries,
                             or ``output_path`` is not an existing directory
        :raises: OSError: if an error occurred decompressing the given container
                          (e.g., empty file, damaged file, etc.)
        """
        self.log(["Decompressing the container into '%s'", output_path])
        if not self.exists():
            self.log_exc(
                "This container does not exist. Wrong path?", None, True, TypeError
            )
        if self.actual_container is None:
            self.log_exc(
                "The actual container object has not been set", None, True, TypeError
            )
        if not os.path.isdir(output_path):
            self.log_exc(
                "The output path is not an existing directory", None, True, ValueError
            )
        if not self.is_safe:
            self.log_exc(
                "This container contains unsafe entries", None, True, ValueError
            )
        self.actual_container.decompress(output_path)

    def compress(self, input_path: str):
        """
        Compress the contents of the given directory.

        :param string input_path: path of the input directory
        :raises: TypeError: if the container path has not been set
        :raises: ValueError: if ``input_path`` is not an existing directory
        :raises: OSError: if an error occurred compressing the given container
                          (e.g., empty file, damaged file, etc.)
        """
        self.log(["Compressing '%s' into this container", input_path])

        if self.file_path is None:
            self.log_exc("The container path has not been set", None, True, TypeError)
        if self.actual_container is None:
            self.log_exc(
                "The actual container object has not been set", None, True, TypeError
            )
        if not os.path.isdir(input_path):
            self.log_exc(
                "The input path is not an existing directory", None, True, ValueError
            )
        gf.ensure_parent_directory(input_path)
        self.actual_container.compress(input_path)

    def exists(self) -> bool:
        """
        Return ``True`` if the container has its path set and it exists,
        ``False`` otherwise.

        :rtype: boolean
        """
        return os.path.isfile(self.file_path) or os.path.isdir(self.file_path)

    def _set_actual_container(self):
        """
        Set the actual container, based on the specified container format.

        If the container format is not specified,
        infer it from the (lowercased) extension of the file path.
        If the format cannot be inferred, it is assumed to be
        of type :class:`~aeneas.container.ContainerFormat.UNPACKED`
        (unpacked directory).
        """
        # infer container format
        if self.container_format is None:
            self.log("Inferring actual container format...")
            path_lowercased = self.file_path.lower()
            self.log(["Lowercased file path: '%s'", path_lowercased])
            self.container_format = ContainerFormat.UNPACKED
            for fmt in ContainerFormat:
                if fmt == ContainerFormat.UNPACKED:
                    continue

                if path_lowercased.endswith(fmt.value):
                    self.container_format = fmt
                    break
            self.log("Inferring actual container format... done")
            self.log(["Inferred format: '%s'", self.container_format])

        # set the actual container
        self.log("Setting actual container...")
        class_map = {
            ContainerFormat.ZIP: (_ContainerZIP, None),
            ContainerFormat.EPUB: (_ContainerZIP, None),
            ContainerFormat.TAR: (_ContainerTAR, ""),
            ContainerFormat.TAR_GZ: (_ContainerTAR, ":gz"),
            ContainerFormat.TAR_BZ2: (_ContainerTAR, ":bz2"),
            ContainerFormat.UNPACKED: (_ContainerUnpacked, None),
        }
        actual_class, variant = class_map[self.container_format]
        self.actual_container = actual_class(
            file_path=self.file_path,
            variant=variant,
            rconf=self.rconf,
            logger=self.logger,
        )
        self.log(["Actual container format: '%s'", self.container_format])
        self.log("Setting actual container... done")


class _ContainerTAR(Loggable):
    """
    A TAR container.
    """

    TAG = "ContainerTAR"

    def __init__(self, file_path, variant, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)
        self.file_path = file_path
        self.variant = variant

    @property
    def entries(self):
        try:
            argument = "r" + self.variant
            with tarfile.open(self.file_path, argument) as tar_file:
                result = [e.name for e in tar_file.getmembers() if e.isfile()]
            return sorted(result)
        except Exception as exc:
            self.log_exc("Cannot read entries from TAR file", exc, True, OSError)

    def read_entry(self, entry):
        try:
            argument = "r" + self.variant
            with tarfile.open(self.file_path, argument) as tar_file:
                tar_entry = tar_file.extractfile(entry)
                result = tar_entry.read()
                tar_entry.close()
            return result
        except Exception as exc:
            self.log_exc("Cannot read entry from TAR file", exc, True, OSError)

    def decompress(self, output_path):
        try:
            argument = "r" + self.variant
            with tarfile.open(self.file_path, argument) as tar_file:
                # TODO: Remove when dropping support for Python 3.11.
                if sys.version_info < (3, 12):
                    tar_file.extractall(output_path)
                else:
                    tar_file.extractall(output_path, filter="data")
        except Exception as exc:
            self.log_exc("Cannot decompress TAR file", exc, True, OSError)

    def compress(self, input_path):
        try:
            argument = "w" + self.variant
            with tarfile.open(self.file_path, argument) as tar_file:
                root_len = len(os.path.abspath(input_path))
                for root, dirs, files in os.walk(input_path):
                    archive_root = os.path.abspath(root)[root_len:]
                    for f in files:
                        fullpath = os.path.join(root, f)
                        archive_name = os.path.join(archive_root, f)
                        tar_file.add(name=fullpath, arcname=archive_name)
        except Exception as exc:
            self.log_exc("Cannot compress TAR File", exc, True, OSError)


class _ContainerZIP(Loggable):
    """
    A ZIP container.
    """

    TAG = "ContainerZIP"

    def __init__(self, file_path, variant=None, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)
        self.file_path = file_path

    @property
    def entries(self):
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                result = [e for e in zip_file.namelist() if not e.endswith("/")]
            return sorted(result)
        except Exception as exc:
            self.log_exc("Cannot read entries from ZIP file", exc, True, OSError)

    def read_entry(self, entry):
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                zip_entry = zip_file.open(entry)
                result = zip_entry.read()
                zip_entry.close()
            return result
        except Exception as exc:
            self.log_exc("Cannot read entry from ZIP file", exc, True, OSError)

    def decompress(self, output_path):
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                zip_file.extractall(output_path)
        except Exception as exc:
            self.log_exc("Cannot decompress ZIP file", exc, True, OSError)

    def compress(self, input_path):
        try:
            with zipfile.ZipFile(self.file_path, "w") as zip_file:
                root_len = len(os.path.abspath(input_path))
                for root, dirs, files in os.walk(input_path):
                    archive_root = os.path.abspath(root)[root_len:]
                    for f in files:
                        fullpath = os.path.join(root, f)
                        archive_name = os.path.join(archive_root, f)
                        zip_file.write(fullpath, archive_name)
        except Exception as exc:
            self.log_exc("Cannot compress ZIP file", exc, True, OSError)


class _ContainerUnpacked(Loggable):
    """
    An unpacked container.
    """

    TAG = "ContainerUnpacked"

    def __init__(self, file_path, variant=None, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)
        self.file_path = file_path

    @property
    def entries(self):
        try:
            result = []
            root_len = len(os.path.abspath(self.file_path))
            for current_dir, dirs, files in os.walk(self.file_path):
                current_dir_abs = os.path.abspath(current_dir)
                for f in files:
                    relative_path = os.path.join(current_dir_abs, f)[(root_len + 1) :]
                    result.append(relative_path)
            return sorted(result)
        except Exception as exc:
            self.log_exc("Cannot read entries from unpacked", exc, True, OSError)

    def read_entry(self, entry):
        try:
            with open(os.path.join(self.file_path, entry), "rb") as unpacked_entry:
                result = unpacked_entry.read()
            return result
        except Exception as exc:
            self.log_exc("Cannot read entry from unpacked", exc, True, OSError)

    def decompress(self, output_path):
        try:
            if os.path.abspath(output_path) == os.path.abspath(self.file_path):
                return
            gf.copytree(self.file_path, output_path)
        except Exception as exc:
            self.log_exc("Cannot decompress unpacked", exc, True, OSError)

    def compress(self, input_path):
        try:
            if os.path.abspath(input_path) == os.path.abspath(self.file_path):
                return
            gf.copytree(input_path, self.file_path)
        except Exception as exc:
            self.log_exc("Cannot compress unpacked", exc, True, OSError)
