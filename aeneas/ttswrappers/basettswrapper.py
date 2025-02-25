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

* :class:`~aeneas.ttswrappers.basettswrapper.TTSCache`,
  a TTS cache;
* :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`,
  an abstract wrapper for a TTS engine.
"""

import contextlib
import logging
import subprocess
import tempfile
import typing

from aeneas.audiofile import AudioFile, AudioFileUnsupportedFormatError
from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class TTSCache(Configurable):
    """
    A TTS cache, that is,
    a dictionary whose keys are pairs
    ``(fragment_language, fragment_text)``
    and whose values are pairs
    ``(file_handler, file_path)``.

    An item in the cache means that the text of the key
    has been synthesized to the file
    located at the path of the corresponding value.

    Note that it is not enough to store
    the string of the text as the key,
    since the same text might be pronounced in a different language.

    Also note that the values also store the file handler,
    since we might want to close it explicitly
    before removing the file from disk.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    def __init__(self, rconf=None):
        super().__init__(rconf=rconf)
        self._initialize_cache()

    def _initialize_cache(self):
        self.cache = dict()
        logger.debug("Cache initialized")

    def __len__(self):
        return len(self.cache)

    def keys(self):
        """
        Return the sorted list of keys currently in the cache.

        :rtype: list of tuples ``(language, text)``
        """
        return sorted(list(self.cache.keys()))

    def is_cached(self, fragment_info):
        """
        Return ``True`` if the given ``(language, text)`` key
        is present in the cache, or ``False`` otherwise.

        :rtype: bool
        """
        return fragment_info in self.cache

    def add(self, fragment_info, file_info):
        """
        Add the given ``(key, value)`` pair to the cache.

        :param fragment_info: the text key
        :type  fragment_info: tuple of str ``(language, text)``
        :param file_info: the path value
        :type  file_info: tuple ``(handler, path)``
        :raises: ValueError if the key is already present in the cache
        """
        if self.is_cached(fragment_info):
            raise ValueError("Attempt to add text already cached")
        self.cache[fragment_info] = file_info

    def get(self, fragment_info):
        """
        Get the value associated with the given key.

        :param fragment_info: the text key
        :type  fragment_info: tuple of str ``(language, text)``
        :raises: KeyError if the key is not present in the cache
        """
        if not self.is_cached(fragment_info):
            raise KeyError("Attempt to get text not cached")
        return self.cache[fragment_info]

    def clear(self):
        """
        Clear the cache and remove all the files from disk.
        """
        logger.debug("Clearing cache...")
        for file_handler, file_info in self.cache.values():
            logger.debug("  Removing file %r", file_info)
            gf.delete_file(file_handler, file_info)
        self._initialize_cache()
        logger.debug("Clearing cache... done")


class BaseTTSWrapper(Configurable):
    """
    An abstract wrapper for a TTS engine.

    It calls the TTS executable or library, passing parameters
    like the text string and languages, and it produces
    a WAVE file on disk and a list of time anchors.

    In case of multiple text fragments, the resulting WAVE files
    will be joined together in a single WAVE file.

    The TTS parameters, their order, and the switches
    can be configured in the concrete subclass
    for a specific TTS engine.

    For example, it might perform one or more calls like ::

        $ echo "text" | tts -v voice_code -w output_file.wav
        or
        $ tts -eval "(voice_code)" -i text_file.txt -o output_file.wav

    The call methods will be attempted in the following order:

        1. direct Python call
        2. Python C extension
        3. TTS executable via ``subprocess``

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :raises: NotImplementedError: if none of the call methods is available
    """

    CLI_PARAMETER_TEXT_PATH = "TEXT_PATH"
    """
    Placeholder to specify the path to the UTF-8 encoded file
    containing the text to be synthesized,
    to be read by the TTS engine.
    """

    CLI_PARAMETER_TEXT_STDIN = "TEXT_STDIN"
    """
    Placeholder to specify that the TTS engine
    reads the text to be synthesized from stdin.
    """

    CLI_PARAMETER_VOICE_CODE_FUNCTION = "VOICE_CODE_FUNCTION"
    """
    Placeholder to specify a list of arguments
    for the TTS engine to select the TTS voice
    to be used for synthesizing the text.
    """

    CLI_PARAMETER_VOICE_CODE_STRING = "VOICE_CODE_STRING"
    """
    Placeholder for the voice code string.
    """

    CLI_PARAMETER_WAVE_PATH = "WAVE_PATH"
    """
    Placeholder to specify the path to the audio file
    to be synthesized by the TTS engine.
    """

    CLI_PARAMETER_WAVE_STDOUT = "WAVE_STDOUT"
    """
    Placeholder to specify that the TTS engine
    outputs the audio data to stdout.
    """

    LANGUAGE_TO_VOICE_CODE: typing.Mapping[str, str] = {}
    """
    Map a language code to a voice code.
    Concrete subclasses must populate this class field,
    according to the language and voice codes
    supported by the TTS engine they wrap.
    """

    CODE_TO_HUMAN: typing.Mapping[str, str] = {}
    """
    Map from voice code to human-readable name.
    """

    CODE_TO_HUMAN_LIST: list[str] = []
    """
    List of all language codes with their human-readable names.
    """

    OUTPUT_AUDIO_FORMAT: typing.ClassVar[tuple[str, int, int] | None] = None
    """
    A tuple ``(codec, channels, rate)``
    specifying the format
    of the audio file generated by the TTS engine,
    for example ``("pcm_s16le", 1, 22050)``.
    If unknown, set it to ``None``:
    in this case, the audio file will be converted
    to PCM16 mono WAVE (RIFF) as needed.
    """

    DEFAULT_LANGUAGE: typing.ClassVar[Language | str | None] = None
    """
    The default language for this TTS engine.
    Concrete subclasses must populate this class field,
    according to the languages supported
    by the TTS engine they wrap.
    """

    DEFAULT_TTS_PATH: typing.ClassVar[str | None] = None
    """
    The default path for this TTS engine,
    when called via ``subprocess``,
    otherwise set it to ``None``.
    """

    HAS_SUBPROCESS_CALL = False
    """
    If ``True``, the TTS wrapper can invoke the TTS engine
    via ``subprocess``.
    """

    HAS_C_EXTENSION_CALL = False
    """
    If ``True``, the TTS wrapper can invoke the TTS engine
    via a C extension call.
    """

    HAS_PYTHON_CALL = False
    """
    If ``True``, the TTS wrapper can invoke the TTS engine
    via a direct Python call.
    """

    C_EXTENSION_NAME = ""
    """
    If the TTS wrapper can invoke the TTS engine
    via a C extension call,
    set here the name of the corresponding Python C/C++ extension.
    """

    def __init__(self, rconf=None):
        if not (
            self.HAS_SUBPROCESS_CALL
            or self.HAS_C_EXTENSION_CALL
            or self.HAS_PYTHON_CALL
        ):
            raise NotImplementedError(
                "You must implement at least one call method: subprocess, C extension, or Python"
            )

        super().__init__(rconf=rconf)

        self.subprocess_arguments = []

        self.tts_path = self.rconf[RuntimeConfiguration.TTS_PATH]
        if self.tts_path is None:
            logger.debug("No tts_path specified in rconf, setting default TTS path")
            self.tts_path = self.DEFAULT_TTS_PATH

        self.use_cache = self.rconf[RuntimeConfiguration.TTS_CACHE]
        self.cache = TTSCache(rconf=rconf) if self.use_cache else None
        logger.debug("TTS path is             %s", self.tts_path)
        logger.debug("TTS cache?              %s", self.use_cache)
        logger.debug("Has Python      call?   %s", self.HAS_PYTHON_CALL)
        logger.debug("Has C extension call?   %s", self.HAS_C_EXTENSION_CALL)
        logger.debug("Has subprocess  call?   %s", self.HAS_SUBPROCESS_CALL)

    def _language_to_voice_code(self, language):
        """
        Translate a language value to a voice code.

        If you want to mock support for a language
        by using a voice for a similar language,
        please add it to the ``LANGUAGE_TO_VOICE_CODE`` dictionary.

        :param language: the requested language
        :type  language: :class:`~aeneas.language.Language`
        :rtype: string
        """
        voice_code = self.rconf[RuntimeConfiguration.TTS_VOICE_CODE]
        if voice_code is None:
            try:
                voice_code = self.LANGUAGE_TO_VOICE_CODE[language]
            except KeyError:
                logger.exception(
                    "Language code %r not found in LANGUAGE_TO_VOICE_CODE",
                    language,
                )
                logger.warning("Using the language code as the voice code")
                voice_code = language
        else:
            logger.debug("TTS voice override in rconf")
        logger.debug("Language to voice code: %r => %r", language, voice_code)
        return voice_code

    def _voice_code_to_subprocess(self, voice_code):
        """
        Convert the ``voice_code`` to a list of parameters
        used when calling the TTS via subprocess.
        """
        return []

    def clear_cache(self):
        """
        Clear the TTS cache, removing all cache files from disk.

        .. versionadded:: 1.6.0
        """
        if self.use_cache:
            logger.debug("Requested to clear TTS cache")
            self.cache.clear()

    def set_subprocess_arguments(self, subprocess_arguments):
        """
        Set the list of arguments that the wrapper will pass to ``subprocess``.

        Placeholders ``CLI_PARAMETER_*`` can be used, and they will be replaced
        by actual values in the ``_synthesize_multiple_subprocess()`` and
        ``_synthesize_single_subprocess()`` built-in functions.
        Literal parameters will be passed unchanged.

        The list should start with the path to the TTS engine.

        This function should be called in the constructor
        of concrete subclasses.

        :param list subprocess_arguments: the list of arguments to be passed to
                                          the TTS engine via subprocess
        """
        # NOTE this is a method because we might need to access self.rconf,
        #      so we cannot specify the list of arguments as a class field
        self.subprocess_arguments = subprocess_arguments
        logger.debug("Subprocess arguments: %s", subprocess_arguments)

    def synthesize_multiple(
        self, text_file, output_file_path, quit_after=None, backwards=False
    ):
        """
        Synthesize the text contained in the given fragment list
        into a WAVE file.

        Return a tuple (anchors, total_time, num_chars).

        Concrete subclasses must implement at least one
        of the following private functions:

            1. ``_synthesize_multiple_python()``
            2. ``_synthesize_multiple_c_extension()``
            3. ``_synthesize_multiple_subprocess()``

        :param text_file: the text file to be synthesized
        :type  text_file: :class:`~aeneas.textfile.TextFile`
        :param string output_file_path: the path to the output audio file
        :param quit_after: stop synthesizing as soon as
                                 reaching this many seconds
        :type quit_after: :class:`~aeneas.exacttiming.TimeValue`
        :param bool backwards: if > 0, synthesize from the end of the text file
        :rtype: tuple (anchors, total_time, num_chars)
        :raises: TypeError: if ``text_file`` is ``None`` or
                            one of the text fragments is not a Unicode string
        :raises: ValueError: if ``self.rconf[RuntimeConfiguration.ALLOW_UNLISTED_LANGUAGES]`` is ``False``
                             and a fragment has a language code not supported by the TTS engine, or
                             if ``text_file`` has no fragments or all its fragments are empty
        :raises: OSError: if output file cannot be written to ``output_file_path``
        :raises: RuntimeError: if both the C extension and
                               the pure Python code did not succeed.
        """
        if text_file is None:
            raise TypeError("`text_file` is None")
        if len(text_file) < 1:
            raise ValueError("The text file has no fragments")
        if text_file.chars == 0:
            raise ValueError("All fragments in the text file are empty")
        if not self.rconf[RuntimeConfiguration.ALLOW_UNLISTED_LANGUAGES]:
            for fragment in text_file.fragments:
                if fragment.language not in self.LANGUAGE_TO_VOICE_CODE:
                    raise ValueError(
                        f"Language {fragment.language!r} is not supported by the selected TTS engine",
                    )
        for fragment in text_file.fragments:
            for line in fragment.lines:
                if not isinstance(line, str):
                    raise TypeError(
                        "The text file contain a line which is not a string"
                    )

        # log parameters
        if quit_after is not None:
            logger.debug("Quit after reaching %.3f", quit_after)
        if backwards:
            logger.debug("Synthesizing backwards")

        # check that output_file_path can be written
        # if not gf.file_can_be_written(output_file_path):
        # raise OSError(f"Cannot write to output file {output_file_path!r}")

        # first, call Python function _synthesize_multiple_python() if available
        if self.HAS_PYTHON_CALL:
            logger.debug("Calling TTS engine via Python")
            try:
                computed, result = self._synthesize_multiple_python(
                    text_file, output_file_path, quit_after, backwards
                )
                if computed:
                    logger.debug(
                        "The _synthesize_multiple_python call was successful, returning anchors"
                    )
                    return result
                else:
                    logger.debug("The _synthesize_multiple_python call failed")
            except Exception:
                logger.exception(
                    "An unexpected error occurred while calling _synthesize_multiple_python",
                )

        # call _synthesize_multiple_c_extension() or _synthesize_multiple_subprocess()
        logger.debug("Calling TTS engine via C extension or subprocess")
        c_extension_function = (
            self._synthesize_multiple_c_extension if self.HAS_C_EXTENSION_CALL else None
        )
        subprocess_function = (
            self._synthesize_multiple_subprocess if self.HAS_SUBPROCESS_CALL else None
        )
        return gf.run_c_extension_with_fallback(
            logger.debug,
            self.C_EXTENSION_NAME,
            c_extension_function,
            subprocess_function,
            (text_file, output_file_path, quit_after, backwards),
            rconf=self.rconf,
        )

    def _synthesize_multiple_python(
        self, text_file, output_file_path, quit_after=None, backwards=False
    ):
        """
        Synthesize multiple fragments via a Python call.

        :rtype: tuple (result, (anchors, current_time, num_chars))
        """
        logger.debug("Synthesizing multiple via a Python call...")
        ret = self._synthesize_multiple_generic(
            helper_function=self._synthesize_single_python_helper,
            text_file=text_file,
            output_file_path=output_file_path,
            quit_after=quit_after,
            backwards=backwards,
        )
        logger.debug("Synthesizing multiple via a Python call... done")
        return ret

    def _synthesize_single_python_helper(
        self, text, voice_code, output_file_path=None, return_audio_data=True
    ):
        """
        This is an helper function to synthesize a single text fragment via a Python call.

        If ``output_file_path`` is ``None``,
        the audio data will not persist to file at the end of the method.

        If ``return_audio_data`` is ``True``,
        return the audio data at the end of the function call;
        if ``False``, just return ``(True, None)`` in case of success.

        :rtype: tuple (result, (duration, sample_rate, codec, data)) or (result, None)
        """
        raise NotImplementedError(
            "This function must be implemented in concrete subclasses supporting Python call"
        )

    def _synthesize_multiple_c_extension(
        self, text_file, output_file_path, quit_after=None, backwards=False
    ):
        """
        Synthesize multiple fragments via a Python C extension.

        :rtype: tuple (result, (anchors, current_time, num_chars))
        """
        raise NotImplementedError(
            "This function must be implemented in concrete subclasses supporting C extension call"
        )

    def _synthesize_single_c_extension_helper(
        self, text, voice_code, output_file_path=None
    ):
        """
        This is an helper function to synthesize a single text fragment via a Python C extension.

        If ``output_file_path`` is ``None``,
        the audio data will not persist to file at the end of the method.

        :rtype: tuple (result, (duration, sample_rate, codec, data))
        """
        raise NotImplementedError(
            "This function might be implemented in concrete subclasses supporting C extension call"
        )

    def _synthesize_multiple_subprocess(
        self, text_file, output_file_path, quit_after=None, backwards=False
    ):
        """
        Synthesize multiple fragments via ``subprocess``.

        :rtype: tuple (result, (anchors, current_time, num_chars))
        """
        logger.debug("Synthesizing multiple via subprocess...")
        ret = self._synthesize_multiple_generic(
            helper_function=self._synthesize_single_subprocess_helper,
            text_file=text_file,
            output_file_path=output_file_path,
            quit_after=quit_after,
            backwards=backwards,
        )
        logger.debug("Synthesizing multiple via subprocess... done")
        return ret

    def _synthesize_single_subprocess_helper(
        self, text, voice_code, output_file_path=None, return_audio_data=True
    ):
        """
        This is an helper function to synthesize a single text fragment via ``subprocess``.

        If ``output_file_path`` is ``None``,
        the audio data will not persist to file at the end of the method.

        If ``return_audio_data`` is ``True``,
        return the audio data at the end of the function call;
        if ``False``, just return ``(True, None)`` in case of success.

        :rtype: tuple (result, (duration, sample_rate, codec, data)) or (result, None)
        """
        # return zero if text is the empty string
        if not text:
            #
            # NOTE sample_rate, codec, data do not matter
            #      if the duration is 0.000 => set them to None
            #
            logger.debug("`text` is empty: returning 0.000")
            return (True, (TimeValue("0.000"), None, None, None))

        with contextlib.ExitStack() as exit_stack:
            # create a temporary output file if needed
            synt_tmp_file = output_file_path is None
            if synt_tmp_file:
                logger.debug(
                    "Synthesizer helper called with output_file_path=None => creating temporary output file"
                )
                tmp_output_file = tempfile.NamedTemporaryFile(
                    suffix=".wav", dir=self.rconf[RuntimeConfiguration.TMP_PATH]
                )
                exit_stack.enter_context(tmp_output_file)
                output_file_path = tmp_output_file.name

                logger.debug("Temporary output file path is %r", output_file_path)

            try:
                # if the TTS engine reads text from file,
                # write the text into a temporary file
                if self.CLI_PARAMETER_TEXT_PATH in self.subprocess_arguments:
                    logger.debug("TTS engine reads text from file")

                    tmp_text_file = tempfile.NamedTemporaryFile(
                        suffix=".txt",
                        mode="w",
                        encoding="utf-8",
                        dir=self.rconf[RuntimeConfiguration.TMP_PATH],
                    )
                    exit_stack.enter_context(tmp_text_file)
                    tmp_text_file_path = tmp_text_file.name

                    logger.debug(
                        "Creating temporary text file %r...", tmp_text_file_path
                    )
                    tmp_text_file.write(text)
                    tmp_text_file.flush()
                    logger.debug(
                        "Creating temporary text file %r... done",
                        tmp_text_file_path,
                    )
                else:
                    logger.debug("TTS engine reads text from stdin")
                    tmp_text_file_path = None

                # copy all relevant arguments
                logger.debug("Creating arguments list...")
                arguments = []
                for arg in self.subprocess_arguments:
                    if arg == self.CLI_PARAMETER_VOICE_CODE_FUNCTION:
                        arguments.extend(self._voice_code_to_subprocess(voice_code))
                    elif arg == self.CLI_PARAMETER_VOICE_CODE_STRING:
                        arguments.append(voice_code)
                    elif arg == self.CLI_PARAMETER_TEXT_PATH:
                        arguments.append(tmp_text_file_path)
                    elif arg == self.CLI_PARAMETER_WAVE_PATH:
                        arguments.append(output_file_path)
                    elif arg == self.CLI_PARAMETER_TEXT_STDIN:
                        # placeholder, do not append
                        pass
                    elif arg == self.CLI_PARAMETER_WAVE_STDOUT:
                        # placeholder, do not append
                        pass
                    else:
                        arguments.append(arg)
                logger.debug("Creating arguments list... done")

                # actual call via subprocess
                logger.debug("Calling TTS engine...")
                logger.debug("Calling with arguments %r", arguments)
                logger.debug("Calling with text %r", text)
                proc = subprocess.Popen(
                    arguments,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )
                if self.CLI_PARAMETER_TEXT_STDIN in self.subprocess_arguments:
                    logger.debug("Passing text via stdin...")
                    (stdoutdata, stderrdata) = proc.communicate(input=text)
                    logger.debug("Passing text via stdin... done")
                else:
                    logger.debug("Passing text via file...")
                    (stdoutdata, stderrdata) = proc.communicate()
                    logger.debug("Passing text via file... done")
                proc.stdout.close()
                proc.stdin.close()
                proc.stderr.close()

                if self.CLI_PARAMETER_WAVE_STDOUT in self.subprocess_arguments:
                    logger.debug("TTS engine wrote audio data to stdout")
                    logger.debug("Writing audio data to file %r...", output_file_path)
                    with open(output_file_path, "wb") as output_file:
                        output_file.write(stdoutdata)
                    logger.debug(
                        "Writing audio data to file %r... done", output_file_path
                    )
                else:
                    logger.debug("TTS engine wrote audio data to file")

                logger.debug("Calling TTS ... done")
            except Exception:
                logger.exception(
                    "An unexpected error occurred while calling TTS engine via subprocess",
                )
                return (False, None)

            # read audio data
            ret = (
                self._read_audio_data(output_file_path)
                if return_audio_data
                else (True, None)
            )

            # return audio data or (True, None)
            return ret

    def _read_audio_data(self, file_path):
        """
        Read audio data from file.

        :rtype: tuple (True, (duration, sample_rate, codec, data)) or (False, None) on exception
        """
        try:
            logger.debug("Reading audio data...")
            # if we know the TTS outputs to PCM16 mono WAVE
            # with the correct sample rate,
            # we can read samples directly from it,
            # without an intermediate conversion through ffmpeg
            audio_file = AudioFile(
                file_path=file_path,
                file_format=self.OUTPUT_AUDIO_FORMAT,
                rconf=self.rconf,
            )
            audio_file.read_samples_from_file()
            logger.debug("Duration of %r: %f", file_path, audio_file.audio_length)
            logger.debug("Reading audio data... done")
            return (
                True,
                (
                    audio_file.audio_length,
                    audio_file.audio_sample_rate,
                    audio_file.audio_format,
                    audio_file.audio_samples,
                ),
            )
        except (AudioFileUnsupportedFormatError, OSError):
            logger.exception("An unexpected error occurred while reading audio data")
            return (False, None)

    def _synthesize_multiple_generic(
        self,
        helper_function,
        text_file,
        output_file_path,
        quit_after=None,
        backwards=False,
    ):
        """
        Synthesize multiple fragments, generic function.

        The ``helper_function`` is a function that takes parameters
        ``(text, voice_code, output_file_path)``
        and returns a tuple
        ``(result, (audio_length, audio_sample_rate, audio_format, audio_samples))``.

        :rtype: tuple (result, (anchors, current_time, num_chars))
        """
        logger.debug("Calling TTS engine using multiple generic function...")

        # get sample rate and codec
        logger.debug("Determining codec and sample rate...")
        if (self.OUTPUT_AUDIO_FORMAT is None) or (len(self.OUTPUT_AUDIO_FORMAT) != 3):
            logger.debug("Determining codec and sample rate with dummy text...")
            succeeded, data = helper_function(
                text="Dummy text to get sample_rate",
                voice_code=self._language_to_voice_code(self.DEFAULT_LANGUAGE),
                output_file_path=None,
            )
            if not succeeded:
                logger.critical("An unexpected error occurred in helper_function")
                return (False, None)
            du_nu, sample_rate, codec, da_nu = data
            logger.debug("Determining codec and sample rate with dummy text... done")
        else:
            logger.debug("Reading codec and sample rate from OUTPUT_AUDIO_FORMAT")
            codec, channels_nu, sample_rate = self.OUTPUT_AUDIO_FORMAT
        logger.debug("Determining codec and sample rate... done")
        logger.debug("  codec:       %s", codec)
        logger.debug("  sample rate: %d", sample_rate)

        # open output file
        output_file = AudioFile(rconf=self.rconf)
        output_file.audio_format = codec
        output_file.audio_channels = 1
        output_file.audio_sample_rate = sample_rate

        # create output
        anchors = []
        current_time = TimeValue("0.000")
        num_chars = 0
        fragments = text_file.fragments
        if backwards:
            fragments = fragments[::-1]
        loop_function = self._loop_use_cache if self.use_cache else self._loop_no_cache
        for num, fragment in enumerate(fragments):
            succeeded, data = loop_function(
                helper_function=helper_function, num=num, fragment=fragment
            )
            if not succeeded:
                logger.critical("An unexpected error occurred in loop_function")
                return (False, None)
            duration, sr_nu, enc_nu, samples = data
            # store for later output
            anchors.append([current_time, fragment.identifier, fragment.text])
            # increase the character counter
            num_chars += fragment.characters
            # concatenate new samples
            logger.debug("Fragment %d starts at: %.3f", num, current_time)
            if duration > 0:
                logger.debug("Fragment %d duration: %.3f", num, duration)
                current_time += duration
                output_file.add_samples(samples, reverse=backwards)
            else:
                logger.debug("Fragment %d has zero duration", num)
            # check if we must stop synthesizing because we have enough audio
            if (quit_after is not None) and (current_time > quit_after):
                logger.debug("Quitting after reached duration %.3f", current_time)
                break

        # minimize memory
        logger.debug("Minimizing memory...")
        output_file.minimize_memory()
        logger.debug("Minimizing memory... done")

        # if backwards, we need to reverse the audio samples again
        if backwards:
            logger.debug("Reversing audio samples...")
            output_file.reverse()
            logger.debug("Reversing audio samples... done")

        # write output file
        logger.debug("Writing audio file %r", output_file_path)
        output_file.write(file_path=output_file_path)

        # return output
        if backwards:
            logger.warning(
                "Please note that anchor time values do not make sense since backwards=True"
            )
        logger.debug("Returning %d time anchors", len(anchors))
        logger.debug("Current time %.3f", current_time)
        logger.debug("Synthesized %d characters", num_chars)
        logger.debug("Calling TTS engine using multiple generic function... done")
        return (True, (anchors, current_time, num_chars))

    def _loop_no_cache(self, helper_function, num, fragment):
        """Synthesize all fragments without using the cache"""
        logger.debug("Examining fragment %d (no cache)...", num)
        # synthesize and get the duration of the output file
        voice_code = self._language_to_voice_code(fragment.language)
        logger.debug("Calling helper function")
        succeeded, data = helper_function(
            text=fragment.filtered_text,
            voice_code=voice_code,
            output_file_path=None,
            return_audio_data=True,
        )
        # check output
        if not succeeded:
            logger.critical("An unexpected error occurred in helper_function")
            return (False, None)
        logger.debug("Examining fragment %d (no cache)... done", num)
        return (True, data)

    def _loop_use_cache(self, helper_function, num, fragment):
        """Synthesize all fragments using the cache"""
        logger.debug("Examining fragment %d (cache)...", num)
        fragment_info = (fragment.language, fragment.filtered_text)
        if self.cache.is_cached(fragment_info):
            logger.debug("Fragment cached: retrieving audio data from cache")

            # read data from file, whose path is in the cache
            file_handler, file_path = self.cache.get(fragment_info)
            logger.debug("Reading cached fragment at %r...", file_path)
            succeeded, data = self._read_audio_data(file_path)
            if not succeeded:
                logger.critical(
                    "An unexpected error occurred while reading cached audio file"
                )
                return (False, None)
            logger.debug("Reading cached fragment at %r... done", file_path)
        else:
            logger.debug("Fragment not cached: synthesizing and caching")

            # creating destination file
            file_info = gf.tmp_file(
                suffix=".cache.wav", root=self.rconf[RuntimeConfiguration.TMP_PATH]
            )
            file_handler, file_path = file_info
            logger.debug("Synthesizing fragment to %r...", file_path)

            # synthesize and get the duration of the output file
            voice_code = self._language_to_voice_code(fragment.language)
            logger.debug("Calling helper function")
            succeeded, data = helper_function(
                text=fragment.filtered_text,
                voice_code=voice_code,
                output_file_path=file_path,
                return_audio_data=True,
            )
            # check output
            if not succeeded:
                logger.critical("An unexpected error occurred in helper_function")
                return (False, None)
            logger.debug("Synthesizing fragment to %r... done", file_path)
            duration, sr_nu, enc_nu, samples = data
            if duration > 0:
                logger.debug("Fragment has > 0 duration, adding it to cache")
                self.cache.add(fragment_info, file_info)
                logger.debug("Added fragment to cache")
            else:
                logger.debug("Fragment has zero duration, not adding it to cache")
            logger.debug(
                "Closing file handler for cached output file path %r", file_path
            )
            gf.close_file_handler(file_handler)
        logger.debug("Examining fragment %d (cache)... done", num)
        return (True, data)
