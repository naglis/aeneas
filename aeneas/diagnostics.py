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

* :class:`~aeneas.diagnostics.Diagnostics`,
  checking whether the setup of ``aeneas`` was successful.

This module can be executed from command line with::

    python -m aeneas.diagnostics

.. versionadded:: 1.4.1
"""

import contextlib
import sys
import tempfile

import aeneas.globalfunctions as gf
import aeneas.globalconstants as gc


class Diagnostics:
    """
    Check whether the setup of ``aeneas`` was successful.
    """

    @classmethod
    def check_shell_encoding(cls):
        """
        Check whether ``sys.stdin`` and ``sys.stdout`` are UTF-8 encoded.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        is_in_utf8 = sys.stdin.encoding in gc.UTF8_ENCODING_VARIANTS
        is_out_utf8 = sys.stdout.encoding in gc.UTF8_ENCODING_VARIANTS
        if is_in_utf8 and is_out_utf8:
            gf.print_success("shell encoding OK")
        else:
            gf.print_warning("shell encoding WARNING")
            if not is_in_utf8:
                gf.print_warning(
                    "  The default input encoding of your shell is not UTF-8"
                )
            if not is_out_utf8:
                gf.print_warning(
                    "  The default output encoding of your shell is not UTF-8"
                )
            gf.print_info("  If you plan to use aeneas on the command line,")
            if gf.is_posix():
                gf.print_info(
                    "  you might want to 'export PYTHONIOENCODING=UTF-8' in your shell"
                )
            else:
                gf.print_info(
                    "  you might want to 'set PYTHONIOENCODING=UTF-8' in your shell"
                )
            return True
        return False

    @classmethod
    def check_ffprobe(cls):
        """
        Check whether ``ffprobe`` can be called.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        try:
            from aeneas.ffprobewrapper import FFPROBEWrapper

            file_path = gf.absolute_path("tools/res/audio.mp3", __file__)
            prober = FFPROBEWrapper()
            prober.read_properties(file_path)
            gf.print_success("ffprobe        OK")
        except Exception:
            gf.print_error("ffprobe        ERROR")
            gf.print_info("  Please make sure you have ffprobe installed correctly")
            gf.print_info("  (usually it is provided by the ffmpeg installer)")
            gf.print_info("  and that its path is in your PATH environment variable")
            return True
        else:
            return False

    @classmethod
    def check_ffmpeg(cls):
        """
        Check whether ``ffmpeg`` can be called.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        with contextlib.suppress(Exception):
            from aeneas.ffmpegwrapper import FFMPEGWrapper

            input_file_path = gf.absolute_path("tools/res/audio.mp3", __file__)
            converter = FFMPEGWrapper()
            with tempfile.NamedTemporaryFile(
                prefix="aeneas.diagnostics.", suffix=".wav"
            ) as tmp_file:
                result = converter.convert(input_file_path, tmp_file.name)
            if result:
                gf.print_success("ffmpeg         OK")
                return False
        gf.print_error("ffmpeg         ERROR")
        gf.print_info("  Please make sure you have ffmpeg installed correctly")
        gf.print_info("  and that its path is in your PATH environment variable")
        return True

    @classmethod
    def check_espeak(cls):
        """
        Check whether ``espeak`` can be called.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        try:
            from aeneas.textfile import TextFile
            from aeneas.textfile import TextFragment
            from aeneas.ttswrappers.espeakttswrapper import ESPEAKTTSWrapper

            text = "From fairest creatures we desire increase,"
            text_file = TextFile()
            text_file.add_fragment(
                TextFragment(language="eng", lines=[text], filtered_lines=[text])
            )
            with tempfile.NamedTemporaryFile(
                prefix="aeneas.diagnostics.", suffix=".wav"
            ) as tmp_file:
                ESPEAKTTSWrapper().synthesize_multiple(text_file, tmp_file.name)
            gf.print_success("espeak         OK")
        except Exception:
            gf.print_error("espeak         ERROR")
            gf.print_info("  Please make sure you have espeak installed correctly")
            gf.print_info("  and that its path is in your PATH environment variable")
            gf.print_info(
                "  You might also want to check that the espeak-data directory"
            )
            gf.print_info(
                "  is set up correctly, for example, it has the correct permissions"
            )
            return True
        else:
            return False

    @classmethod
    def check_tools(cls):
        """
        Check whether ``aeneas.tools.*`` can be imported.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        try:
            # disabling this check, as it requires the optional dependency youtube-dl
            # COMMENTED from aeneas.tools.download import DownloadCLI
            # disabling this check, as it requires the optional dependency Pillow
            # COMMENTED from aeneas.tools.plot_waveform import PlotWaveformCLI
            gf.print_success("aeneas.tools   OK")
        except Exception:
            gf.print_error("aeneas.tools   ERROR")
            gf.print_info("  Unable to import one or more aeneas.tools")
            gf.print_info("  Please check that you installed aeneas properly")
            return True
        else:
            return False

    @classmethod
    def check_cdtw(cls):
        """
        Check whether Python C extension ``cdtw`` can be imported.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        if gf.can_run_c_extension("cdtw"):
            gf.print_success("aeneas.cdtw    AVAILABLE")
            return False
        gf.print_warning("aeneas.cdtw    NOT AVAILABLE")
        gf.print_info("  You can still run aeneas but it will be significantly slower")
        gf.print_info("  Please refer to the installation documentation for details")
        return True

    @classmethod
    def check_cmfcc(cls):
        """
        Check whether Python C extension ``cmfcc`` can be imported.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        if gf.can_run_c_extension("cmfcc"):
            gf.print_success("aeneas.cmfcc   AVAILABLE")
            return False
        gf.print_warning("aeneas.cmfcc   NOT AVAILABLE")
        gf.print_info("  You can still run aeneas but it will be significantly slower")
        gf.print_info("  Please refer to the installation documentation for details")
        return True

    @classmethod
    def check_cengw(cls):
        """
        Check whether Python C extension ``cengw`` can be imported.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        if gf.can_run_c_extension("cengw"):
            gf.print_success("aeneas.cengw   AVAILABLE")
            return False
        gf.print_warning("aeneas.cengw   NOT AVAILABLE")
        gf.print_info("  You can still run aeneas but it will be a bit slower")
        gf.print_info("  Please refer to the installation documentation for details")
        return True

    @classmethod
    def check_cew(cls):
        """
        Check whether Python C extension ``cew`` can be imported.

        Return ``True`` on failure and ``False`` on success.

        :rtype: bool
        """
        if gf.can_run_c_extension("cew"):
            gf.print_success("aeneas.cew     AVAILABLE")
            return False
        gf.print_warning("aeneas.cew     NOT AVAILABLE")
        gf.print_info("  You can still run aeneas but it will be a bit slower")
        gf.print_info("  Please refer to the installation documentation for details")
        return True

    @classmethod
    def check_all(cls, tools=True, encoding=True, c_ext=True):
        """
        Perform all checks.

        Return a tuple of booleans ``(errors, warnings, c_ext_warnings)``.

        :param bool tools: if ``True``, check aeneas tools
        :param bool encoding: if ``True``, check shell encoding
        :param bool c_ext: if ``True``, check Python C extensions
        :rtype: (bool, bool, bool)
        """
        # errors are fatal
        if cls.check_ffprobe():
            return (True, False, False)
        if cls.check_ffmpeg():
            return (True, False, False)
        if cls.check_espeak():
            return (True, False, False)
        if (tools) and (cls.check_tools()):
            return (True, False, False)
        # warnings are non-fatal
        warnings = False
        c_ext_warnings = False
        if encoding:
            warnings = cls.check_shell_encoding()
        if c_ext:
            # we do not want lazy evaluation
            c_ext_warnings = cls.check_cdtw() or c_ext_warnings
            c_ext_warnings = cls.check_cmfcc() or c_ext_warnings
            c_ext_warnings = cls.check_cengw() or c_ext_warnings
            c_ext_warnings = cls.check_cew() or c_ext_warnings
        # return results
        return (False, warnings, c_ext_warnings)


def main():
    errors, warnings, c_ext_warnings = Diagnostics.check_all()
    if errors:
        sys.exit(1)
    if c_ext_warnings:
        gf.print_warning(
            "All required dependencies are met but at least one Python C extension is not available"
        )
        sys.exit(2)
    else:
        gf.print_success(
            "All required dependencies are met and all available Python C extensions are working"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
