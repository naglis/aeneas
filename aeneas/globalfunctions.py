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
Global common functions.
"""

import contextlib
import datetime
import functools
import importlib.util
import math
import os
import re
import shutil
import sys
import typing

from aeneas.exacttiming import TimeValue
import aeneas.globalconstants as gc


# RUNTIME CONSTANTS

# ANSI codes to color output in terminal
ANSI_END = "\033[0m"
ANSI_ERROR = "\033[91m"
ANSI_OK = "\033[92m"
ANSI_WARNING = "\033[93m"

# timing regex patterns
HHMMSS_MMM_PATTERN = re.compile(r"([0-9]*):([0-9]*):([0-9]*)\.([0-9]*)")
HHMMSS_MMM_PATTERN_COMMA = re.compile(r"([0-9]*):([0-9]*):([0-9]*),([0-9]*)")

# True if running from a frozen binary (e.g., compiled with pyinstaller)
FROZEN = getattr(sys, "frozen", False)

# COMMON FUNCTIONS


def safe_print(msg: str):
    """
    Safely print a given Unicode string to stdout,
    possibly replacing characters non-printable
    in the current stdout encoding.

    :param string msg: the message
    """
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            # NOTE encoding and decoding so that in Python 3 no b"..." is printed
            encoded = msg.encode(sys.stdout.encoding, "replace")
            decoded = encoded.decode(sys.stdout.encoding, "replace")
            print(decoded)
        except (UnicodeDecodeError, UnicodeEncodeError):
            print("[ERRO] An unexpected error happened while printing to stdout.")
            print(
                "[ERRO] Please check that your file/string encoding matches the shell encoding."
            )
            print(
                "[ERRO] If possible, set your shell encoding to UTF-8 and convert any files with legacy encodings."
            )


def print_error(msg: str, color: bool = True):
    """
    Print an error message.

    :param string msg: the message
    :param bool color: if ``True``, print with POSIX color
    """
    if color and is_posix():
        safe_print(f"{ANSI_ERROR}[ERRO] {msg}{ANSI_END}")
    else:
        safe_print(f"[ERRO] {msg}")


def print_info(msg: str, color: bool = True):
    """
    Print an info message.

    :param string msg: the message
    :param bool color: if ``True``, print with POSIX color
    """
    safe_print(f"[INFO] {msg}")


def print_success(msg: str, color: bool = True):
    """
    Print a success message.

    :param string msg: the message
    :param bool color: if ``True``, print with POSIX color
    """
    if color and is_posix():
        safe_print(f"{ANSI_OK}[INFO] {msg}{ANSI_END}")
    else:
        safe_print(f"[INFO] {msg}")


def print_warning(msg: str, color: bool = True):
    """
    Print a warning message.

    :param string msg: the message
    :param bool color: if ``True``, print with POSIX color
    """
    if color and is_posix():
        safe_print(f"{ANSI_WARNING}[WARN] {msg}{ANSI_END}")
    else:
        safe_print(f"[WARN] {msg}")


def datetime_string(time_zone: bool = False) -> str:
    """
    Return a string representing the current date and time,
    in ``YYYY-MM-DDThh:mm:ss`` or ``YYYY-MM-DDThh:mm:ss+hh:mm`` format

    :param boolean time_zone: if ``True``, add the time zone offset.

    :rtype: string
    """
    time = datetime.datetime.now()
    template = "%04d-%02d-%02dT%02d:%02d:%02d"
    if time_zone:
        template += "+00:00"
    return template % (
        time.year,
        time.month,
        time.day,
        time.hour,
        time.minute,
        time.second,
    )


def safe_float(string: str, default: float | None = None) -> float | None:
    """
    Safely parse a string into a float.

    On error return the ``default`` value.

    :param string string: string value to be converted
    :param float default: default value to be used in case of failure
    :rtype: float
    """
    value = default
    with contextlib.suppress(TypeError, ValueError):
        value = float(string)
    return value


def safe_int(string: str, default: int | None = None) -> int | None:
    """
    Safely parse a string into an int.

    On error return the ``default`` value.

    :param string string: string value to be converted
    :param int default: default value to be used in case of failure
    :rtype: int
    """
    value = safe_float(string, default)
    if value is not None:
        value = int(value)
    return value


def safe_get(
    dictionary: typing.Mapping[str, typing.Any],
    key: str,
    default_value: typing.Any,
    can_return_none: bool = True,
) -> typing.Any:
    """
    Safely perform a dictionary get,
    returning the default value if the key is not found.

    :param dict dictionary: the dictionary
    :param string key: the key
    :param variant default_value: the default value to be returned
    :param bool can_return_none: if ``True``, the function can return ``None``;
                                 otherwise, return ``default_value`` even if the
                                 dictionary lookup succeeded
    :rtype: variant
    """
    return_value = default_value
    with contextlib.suppress(KeyError, TypeError):
        return_value = dictionary[key]

    if return_value is None and not can_return_none:
        return_value = default_value

    return return_value


def config_string_to_dict(string: str, result=None) -> dict[str, str]:
    """
    Convert a given configuration string ::

        key_1=value_1|key_2=value_2|...|key_n=value_n

    into the corresponding dictionary ::

        dictionary[key_1] = value_1
        dictionary[key_2] = value_2
        ...
        dictionary[key_n] = value_n

    :param string string: the configuration string
    :rtype: dict
    """
    if string is None:
        return {}
    pairs = string.split(gc.CONFIG_STRING_SEPARATOR_SYMBOL)
    return pairs_to_dict(pairs, result)


def pairs_to_dict(pairs: list[str], result=None) -> dict[str, str]:
    """
    Convert a given list of ``key=value`` strings ::

        ["key_1=value_1", "key_2=value_2", ..., "key_n=value_n"]

    into the corresponding dictionary ::

        dictionary[key_1] = value_1
        dictionary[key_2] = value_2
        ...
        dictionary[key_n] = value_n

    :param list pairs: the list of key=value strings
    :rtype: dict
    """
    dictionary = {}
    for pair in pairs:
        if len(pair) == 0:
            continue

        tokens = pair.split(gc.CONFIG_STRING_ASSIGNMENT_SYMBOL)
        if len(tokens) == 2 and len(tokens[0]) > 0 and len(tokens[1]) > 0:
            dictionary[tokens[0]] = tokens[1]
        elif result is not None:
            result.add_warning(f"Invalid key=value string: {pair!r}")
    return dictionary


def copytree(source_directory: str, destination_directory: str, ignore=None):
    """
    Recursively copy the contents of a source directory
    into a destination directory.
    Both directories must exist.

    This function does not copy the root directory ``source_directory``
    into ``destination_directory``.

    Since ``shutil.copytree(src, dst)`` requires ``dst`` not to exist,
    we cannot use for our purposes.

    Code adapted from http://stackoverflow.com/a/12686557

    :param string source_directory: the source directory, already existing
    :param string destination_directory: the destination directory, already existing
    """
    if os.path.isdir(source_directory):
        if not os.path.isdir(destination_directory):
            os.makedirs(destination_directory)
        files = os.listdir(source_directory)
        if ignore is not None:
            ignored = ignore(source_directory, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                copytree(
                    os.path.join(source_directory, f),
                    os.path.join(destination_directory, f),
                    ignore,
                )
    else:
        shutil.copyfile(source_directory, destination_directory)


def ensure_parent_directory(path: str, ensure_parent: bool = True):
    """
    Ensures the parent directory exists.

    :param string path: the path of the file
    :param bool ensure_parent: if ``True``, ensure the parent directory of ``path`` exists;
                               if ``False``, ensure ``path`` exists
    :raises: OSError: if the path cannot be created
    """
    parent_directory = os.path.abspath(path)
    if ensure_parent:
        parent_directory = os.path.dirname(parent_directory)
    if not os.path.exists(parent_directory):
        try:
            os.makedirs(parent_directory)
        except OSError:
            raise OSError(f"Directory {parent_directory!r} cannot be created")


def time_from_ttml(string: str | None) -> TimeValue:
    """
    Parse the given ``SS.mmms`` string
    (TTML values have an "s" suffix, e.g. ``1.234s``)
    and return a time value.

    :param string string: the string to be parsed
    :rtype: :class:`~aeneas.exacttiming.TimeValue`
    """
    if string is None or len(string) < 2:
        return TimeValue("0.000")
    # strips "s" at the end
    string = string[:-1]
    return time_from_ssmmm(string)


def time_to_ttml(time_value: float | None) -> str:
    """
    Format the given time value into a ``SS.mmms`` string
    (TTML values have an "s" suffix, e.g. ``1.234s``).

    Examples: ::

        12        => 12.000s
        12.345    => 12.345s
        12.345432 => 12.345s
        12.345678 => 12.346s

    :param float time_value: a time value, in seconds
    :rtype: string
    """
    if time_value is None:
        time_value = 0.0
    return f"{time_to_ssmmm(time_value)}s"


def time_from_ssmmm(string: str | None) -> TimeValue:
    """
    Parse the given ``SS.mmm`` string and return a time value.

    :param string string: the string to be parsed
    :rtype: :class:`~aeneas.exacttiming.TimeValue`
    """
    return TimeValue(string or "0.000")


def time_to_ssmmm(time_value: float | None) -> str:
    """
    Format the given time value into a ``SS.mmm`` string.

    Examples: ::

        12        => 12.000
        12.345    => 12.345
        12.345432 => 12.345
        12.345678 => 12.346

    :param float time_value: a time value, in seconds
    :rtype: string
    """
    if time_value is None:
        time_value = 0.0
    return f"{time_value:.3f}"


def time_from_hhmmssmmm(string: str, decimal_separator: str = ".") -> TimeValue:
    """
    Parse the given ``HH:MM:SS.mmm`` string and return a time value.

    :param string string: the string to be parsed
    :param string decimal_separator: the decimal separator to be used
    :rtype: :class:`~aeneas.exacttiming.TimeValue`
    """
    if decimal_separator == ",":
        pattern = HHMMSS_MMM_PATTERN_COMMA
    else:
        pattern = HHMMSS_MMM_PATTERN
    v_length = TimeValue("0.000")
    with contextlib.suppress(TypeError):
        if match := pattern.search(string):
            v_h = int(match.group(1))
            v_m = int(match.group(2))
            v_s = int(match.group(3))
            v_f = TimeValue("0." + match.group(4))
            v_length = v_h * 3600 + v_m * 60 + v_s + v_f
    return v_length


def time_to_hhmmssmmm(time_value: float | None, decimal_separator: str = ".") -> str:
    """
    Format the given time value into a ``HH:MM:SS.mmm`` string.

    Examples: ::

        12        => 00:00:12.000
        12.345    => 00:00:12.345
        12.345432 => 00:00:12.345
        12.345678 => 00:00:12.346
        83        => 00:01:23.000
        83.456    => 00:01:23.456
        83.456789 => 00:01:23.456
        3600      => 01:00:00.000
        3612.345  => 01:00:12.345

    :param float time_value: a time value, in seconds
    :param string decimal_separator: the decimal separator, default ``.``
    :rtype: string
    """
    if time_value is None:
        time_value = 0.0
    tmp = time_value
    hours = int(math.floor(tmp / 3600))
    tmp -= hours * 3600
    minutes = int(math.floor(tmp / 60))
    tmp -= minutes * 60
    seconds = int(math.floor(tmp))
    tmp -= seconds
    milliseconds = int(math.floor(tmp * 1000))
    return (
        f"{hours:02d}:{minutes:02d}:{seconds:02d}{decimal_separator}{milliseconds:03d}"
    )


def time_from_srt(string: str) -> TimeValue:
    """
    Parse the given ``HH:MM:SS,mmm`` string and return a time value.

    :param string string: the string to be parsed
    :rtype: :class:`~aeneas.exacttiming.TimeValue`
    """
    return time_from_hhmmssmmm(string, decimal_separator=",")


def time_to_srt(time_value: float) -> str:
    """
    Format the given time value into a ``HH:MM:SS,mmm`` string,
    as used in the SRT format.

    Examples: ::

        12        => 00:00:12,000
        12.345    => 00:00:12,345
        12.345432 => 00:00:12,345
        12.345678 => 00:00:12,346
        83        => 00:01:23,000
        83.456    => 00:01:23,456
        83.456789 => 00:01:23,456
        3600      => 01:00:00,000
        3612.345  => 01:00:12,345

    :param float time_value: a time value, in seconds
    :rtype: string
    """
    return time_to_hhmmssmmm(time_value, decimal_separator=",")


def is_posix() -> bool:
    """
    Return ``True`` if running on a POSIX OS.
    """
    # from https://docs.python.org/2/library/os.html#os.name
    # the registered values of os.name are:
    # "posix", "nt", "os2", "ce", "java", "riscos"
    return os.name == "posix"


def is_windows() -> bool:
    """
    Return ``True`` if running on Windows.
    """
    return os.name == "nt"


def fix_slash(path):
    """
    On non-POSIX OSes, change the slashes in ``path``
    for loading in the browser.

    Example: ::

        c:\\abc\\def => c:/abc/def

    :param string path: the path
    :rtype: string
    """
    if not is_posix():
        path = path.replace("\\", "/")
    return path


def can_run_c_extension(name: str | None = None) -> bool:
    """
    Determine whether the given Python C extension loads correctly.

    If ``name`` is ``None``, tests all Python C extensions,
    and return ``True`` if and only if all load correctly.

    :param string name: the name of the Python C extension to test
    :rtype: bool
    """

    def can_import(name: str) -> bool:
        return importlib.util.find_spec(name) is not None

    # Python C extension for computing DTW.
    can_run_cdtw = functools.partial(can_import, "aeneas.cdtw.cdtw")

    # Python C extension for computing MFCC.
    can_run_cmfcc = functools.partial(can_import, "aeneas.cmfcc.cmfcc")

    # Python C extension for synthesizing with eSpeak.
    can_run_cew = functools.partial(can_import, "aeneas.cew.cew")
    #
    # Python C extension for synthesizing with eSpeak NG.
    can_run_cengw = functools.partial(can_import, "aeneas.cengw.cengw")

    # Python C extension for synthesizing with Festival.
    can_run_cfw = functools.partial(can_import, "aeneas.cfw.cfw")

    if name == "cdtw":
        return can_run_cdtw()
    elif name == "cmfcc":
        return can_run_cmfcc()
    elif name == "cengw":
        return can_run_cengw()
    elif name == "cew":
        return can_run_cew()
    elif name == "cfw":
        return can_run_cfw()
    else:
        # NOTE cfw is still experimental!
        return can_run_cdtw() and can_run_cmfcc() and (can_run_cengw() or can_run_cew())


def run_c_extension_with_fallback(
    log_function, extension: str, c_function, py_function, args, rconf
):
    """
    Run a function calling a C extension, falling back
    to a pure Python function if the former does not succeed.

    :param function log_function: a logger function
    :param string extension: the name of the extension
    :param function c_function: the (Python) function calling the C extension
    :param function py_function: the (Python) function providing the fallback
    :param rconf: the runtime configuration
    :type  rconf: :class:`aeneas.runtimeconfiguration.RuntimeConfiguration`
    :rtype: depends on the extension being called
    :raises: RuntimeError: if both the C extension and
                           the pure Python code did not succeed.

    .. versionadded:: 1.4.0
    """
    computed = False
    if not rconf["c_extensions"]:
        log_function("C extensions disabled")
    elif extension not in rconf:
        log_function("C extension %r not recognized", extension)
    elif not rconf[extension]:
        log_function("C extension %r disabled", extension)
    else:
        log_function("C extension %r enabled", extension)
        if c_function is None:
            log_function("C function is None")
        elif can_run_c_extension(extension):
            log_function("C extension %r enabled and it can be loaded", extension)
            computed, result = c_function(*args)
        else:
            log_function("C extension %r enabled but it cannot be loaded", extension)

    if not computed:
        if py_function is None:
            log_function("Python function is None")
        else:
            log_function("Running the pure Python code")
            computed, result = py_function(*args)

    if not computed:
        raise RuntimeError(
            "Both the C extension and the pure Python code failed. (Wrong arguments? Input too big?)"
        )

    return result


def delete_file(path: str):
    """
    Safely delete file.

    :param string path: the file path
    """
    with contextlib.suppress(Exception):
        os.remove(path)


def relative_path(path: str | None, from_file: str) -> str | None:
    """
    Return the relative path of a file or directory, specified
    as ``path`` relative to (the parent directory of) ``from_file``.

    This method is intented to be called with ``__file__``
    as second argument.

    The returned path is relative to the current working directory.

    If ``path`` is ``None``, return ``None``.

    Example: ::

        path="res/foo.bar"
        from_file="/root/abc/def/ghi.py"
        cwd="/root"
        => "abc/def/res/foo.bar"

    :param string path: the file path
    :param string from_file: the reference file
    :rtype: string
    """
    if path is None:
        return None
    abs_path_target = absolute_path(path, from_file)
    abs_path_cwd = os.getcwd()
    if is_windows():
        # NOTE on Windows, if the two paths are on different drives,
        #      the notion of relative path is not defined:
        #      return the absolute path of the target instead.
        t_drive, t_tail = os.path.splitdrive(abs_path_target)
        c_drive, c_tail = os.path.splitdrive(abs_path_cwd)
        if t_drive != c_drive:
            return abs_path_target
    return os.path.relpath(abs_path_target, start=abs_path_cwd)


def absolute_path(path: str, from_file: str) -> str:
    """
    Return the absolute path of a file or directory, specified
    as ``path`` relative to (the parent directory of) ``from_file``.

    This method is intented to be called with ``__file__``
    as second argument.

    Example: ::

        path="res/foo.bar"
        from_file="/abc/def/ghi.py"
        => "/abc/def/res/foo.bar"

    :param string path: the file path
    :param string from_file: the reference file
    :rtype: string
    """
    current_directory = os.path.dirname(from_file)
    target = os.path.join(current_directory, path)
    return os.path.abspath(target)


def is_utf8_encoded(bstring: bytes) -> bool:
    """
    Return ``True`` if the given byte string can be decoded
    into a Unicode string using the UTF-8 decoder.

    :param bytes bstring: the string to test
    :rtype: bool
    """
    with contextlib.suppress(UnicodeDecodeError):
        bstring.decode("utf-8")
        return True
    return False


def safe_unicode(string: typing.AnyStr | None) -> str | None:
    """
    Safely convert the given string to a Unicode string.

    :param variant string: the byte string or Unicode string to convert
    :rtype: string
    """
    if string is None:
        return None
    if isinstance(string, bytes):
        return string.decode("utf-8")
    return string


def safe_bytes(string: typing.AnyStr | None) -> bytes | None:
    """
    Safely convert the given string to a bytes string.

    :param variant string: the byte string or Unicode string to convert
    :rtype: bytes
    """
    if string is None:
        return None
    if isinstance(string, str):
        return string.encode("utf-8")
    return string


def safe_unicode_stdin(string: typing.AnyStr | None) -> str | None:
    """
    Safely convert the given string to a Unicode string,
    decoding using ``sys.stdin.encoding`` if needed.

    If running from a frozen binary, ``utf-8`` encoding is assumed.

    :param variant string: the byte string or Unicode string to convert
    :rtype: string
    """
    if string is None:
        return None
    if isinstance(string, bytes):
        if FROZEN:
            return string.decode("utf-8")
        try:
            return string.decode(sys.stdin.encoding)
        except UnicodeDecodeError:
            return string.decode(sys.stdin.encoding, "replace")
        except Exception:
            return string.decode("utf-8")
    return string


def with_ns(tag: str, ns: str) -> str:
    """
    Return tag nam with namespace applied.
    """
    return f"{{{ns}}}{tag}"
