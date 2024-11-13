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
Execute a Task, that is, a pair of audio/text files
and a configuration string.
"""

import sys

from aeneas.adjustboundaryalgorithm import AdjustBoundaryAlgorithm
from aeneas.audiofile import AudioFile
from aeneas.downloader import Downloader
from aeneas.exacttiming import Decimal
from aeneas.executetask import ExecuteTask
from aeneas.idsortingalgorithm import IDSortingAlgorithm
from aeneas.language import Language
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.syncmap import SyncMapFormat
from aeneas.syncmap import SyncMapFragment
from aeneas.syncmap import SyncMapHeadTailFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.textfile import TextFileFormat
from aeneas.tools.abstract_cli_program import AbstractCLIProgram
from aeneas.ttswrappers.awsttswrapper import AWSTTSWrapper
from aeneas.ttswrappers.espeakngttswrapper import ESPEAKNGTTSWrapper
from aeneas.ttswrappers.espeakttswrapper import ESPEAKTTSWrapper
from aeneas.ttswrappers.festivalttswrapper import FESTIVALTTSWrapper
from aeneas.ttswrappers.macosttswrapper import MacOSTTSWrapper
from aeneas.ttswrappers.nuancettswrapper import NuanceTTSWrapper
from aeneas.validator import Validator
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf


class ExecuteTaskCLI(AbstractCLIProgram):
    """
    Execute a Task, that is, a pair of audio/text files
    and a configuration string.
    """

    AUDIO_FILE = gf.relative_path("res/audio.mp3", __file__)
    CTW_ESPEAK = gf.relative_path("../extra/ctw_espeak.py", __file__)
    CTW_SPEECT = gf.relative_path("../extra/ctw_speect/ctw_speect.py", __file__)

    DEMOS = {
        "--example-aftercurrent": {
            "description": "input: plain text (plain), output: AUD, aba beforenext 0.200",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=aud|task_adjust_boundary_algorithm=aftercurrent|task_adjust_boundary_aftercurrent_value=0.200",
            "syncmap": "output/sonnet.aftercurrent0200.aud",
            "options": "",
            "show": False,
        },
        "--example-beforenext": {
            "description": "input: plain text (plain), output: AUD, aba beforenext 0.200",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=aud|task_adjust_boundary_algorithm=beforenext|task_adjust_boundary_beforenext_value=0.200",
            "syncmap": "output/sonnet.beforenext0200.aud",
            "options": "",
            "show": False,
        },
        "--example-cewsubprocess": {
            "description": "input: plain text, output: TSV, run via cewsubprocess",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=tsv",
            "syncmap": "output/sonnet.cewsubprocess.tsv",
            "options": '-r="cew_subprocess_enabled=True"',
            "show": False,
        },
        "--example-ctw-espeak": {
            "description": "input: plain text, output: TSV, tts engine: ctw espeak",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=tsv",
            "syncmap": "output/sonnet.ctw_espeak.tsv",
            "options": '-r="tts=custom|tts_path=%s"' % CTW_ESPEAK,
            "show": False,
        },
        "--example-ctw-speect": {
            "description": "input: plain text, output: TSV, tts engine: ctw speect",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=tsv",
            "syncmap": "output/sonnet.ctw_speect.tsv",
            "options": '-r="tts=custom|tts_path=%s"' % CTW_SPEECT,
            "show": False,
        },
        "--example-eaf": {
            "description": "input: plain text, output: EAF",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=eaf",
            "syncmap": "output/sonnet.eaf",
            "options": "",
            "show": True,
        },
        "--example-faster-rate": {
            "description": "input: plain text (plain), output: SRT, print faster than 12.0 chars/s",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rate|task_adjust_boundary_rate_value=12.000",
            "syncmap": "output/sonnet.faster.srt",
            "options": "--faster-rate",
            "show": False,
        },
        "--example-festival": {
            "description": "input: plain text, output: TSV, tts engine: Festival",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng-USA|is_text_type=plain|os_task_file_format=tsv",
            "syncmap": "output/sonnet.festival.tsv",
            "options": '-r="tts=festival"',
            "show": False,
        },
        "--example-flatten-12": {
            "description": "input: mplain text (multilevel), output: JSON, levels to output: 1 and 2",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=json|os_task_file_levels=12",
            "syncmap": "output/sonnet.flatten12.json",
            "options": "",
            "show": False,
        },
        "--example-flatten-2": {
            "description": "input: mplain text (multilevel), output: JSON, levels to output: 2",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=json|os_task_file_levels=2",
            "syncmap": "output/sonnet.flatten2.json",
            "options": "",
            "show": False,
        },
        "--example-flatten-3": {
            "description": "input: mplain text (multilevel), output: JSON, levels to output: 3",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=json|os_task_file_levels=3",
            "syncmap": "output/sonnet.flatten3.json",
            "options": "",
            "show": False,
        },
        "--example-head-tail": {
            "description": "input: plain text, output: TSV, explicit head and tail",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=tsv|is_audio_file_head_length=0.400|is_audio_file_tail_length=0.500|os_task_file_head_tail_format=stretch",
            "syncmap": "output/sonnet.headtail.tsv",
            "options": "",
            "show": False,
        },
        "--example-json": {
            "description": "input: plain text, output: JSON",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=json",
            "syncmap": "output/sonnet.json",
            "options": "",
            "show": True,
        },
        "--example-mplain-json": {
            "description": "input: multilevel plain text (mplain), output: JSON",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=json",
            "syncmap": "output/sonnet.mplain.json",
            "options": "",
            "show": False,
        },
        "--example-mplain-smil": {
            "description": "input: multilevel plain text (mplain), output: SMIL",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=smil|os_task_file_smil_audio_ref=p001.mp3|os_task_file_smil_page_ref=p001.xhtml",
            "syncmap": "output/sonnet.mplain.smil",
            "options": "",
            "show": True,
        },
        "--example-multilevel-tts": {
            "description": "input: multilevel plain text (mplain), different TTS engines, output: JSON",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng-USA|is_text_type=mplain|os_task_file_format=json",
            "syncmap": "output/sonnet.mplain.json",
            "options": '-r="tts_l1=festival|tts_l2=festival|tts_l3=espeak"',
            "show": False,
        },
        "--example-munparsed-json": {
            "description": "input: multilevel unparsed text (munparsed), output: JSON",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/munparsed2.xhtml", __file__),
            "config": "task_language=eng|is_text_type=munparsed|is_text_munparsed_l1_id_regex=p[0-9]+|is_text_munparsed_l2_id_regex=s[0-9]+|is_text_munparsed_l3_id_regex=w[0-9]+|os_task_file_format=json",
            "syncmap": "output/sonnet.munparsed.json",
            "options": "",
            "show": False,
        },
        "--example-munparsed-smil": {
            "description": "input: multilevel unparsed text (munparsed), output: SMIL",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/munparsed.xhtml", __file__),
            "config": "task_language=eng|is_text_type=munparsed|is_text_munparsed_l1_id_regex=p[0-9]+|is_text_munparsed_l2_id_regex=p[0-9]+s[0-9]+|is_text_munparsed_l3_id_regex=p[0-9]+s[0-9]+w[0-9]+|os_task_file_format=smil|os_task_file_smil_audio_ref=p001.mp3|os_task_file_smil_page_ref=p001.xhtml",
            "syncmap": "output/sonnet.munparsed.smil",
            "options": "",
            "show": True,
        },
        "--example-mws": {
            "description": "input: plain text, output: JSON, resolution: 0.500 s",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=json",
            "syncmap": "output/sonnet.mws.json",
            "options": '-r="mfcc_window_length=1.500|mfcc_window_shift=0.500"',
            "show": False,
        },
        "--example-no-zero": {
            "description": "input: multilevel plain text (mplain), output: JSON, no zero duration",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_no_zero=True",
            "syncmap": "output/sonnet.nozero.json",
            "options": "--zero",
            "show": False,
        },
        "--example-offset": {
            "description": "input: plain text (plain), output: AUD, aba offset 0.200",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=aud|task_adjust_boundary_algorithm=offset|task_adjust_boundary_offset_value=0.200",
            "syncmap": "output/sonnet.offset0200.aud",
            "options": "",
            "show": False,
        },
        "--example-percent": {
            "description": "input: plain text (plain), output: AUD, aba percent 50",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=aud|task_adjust_boundary_algorithm=percent|task_adjust_boundary_percent_value=50",
            "syncmap": "output/sonnet.percent50.aud",
            "options": "",
            "show": False,
        },
        "--example-py": {
            "description": "input: plain text, output: JSON, pure python",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=json",
            "syncmap": "output/sonnet.cext.json",
            "options": '-r="c_extensions=False"',
            "show": False,
        },
        "--example-rate": {
            "description": "input: plain text (plain), output: SRT, max rate 14.0 chars/s, print rates",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rate|task_adjust_boundary_rate_value=14.000",
            "syncmap": "output/sonnet.rates.srt",
            "options": "--rate",
            "show": False,
        },
        "--example-remove-nonspeech": {
            "description": "input: plain text (plain), output: SRT, remove nonspeech >=0.500 s",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
            "syncmap": "output/sonnet.remove.nonspeech.srt",
            "options": "",
            "show": False,
        },
        "--example-remove-nonspeech-rateaggressive": {
            "description": "input: plain text (plain), output: SRT, remove nonspeech >=0.500 s, max rate 14.0 chars/s, print rates",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000",
            "syncmap": "output/sonnet.remove.nonspeech.rateaggressive.srt",
            "options": "--rate",
            "show": False,
        },
        "--example-replace-nonspeech": {
            "description": "input: plain text (plain), output: AUD, replace nonspeech >=0.500 s with (sil)",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=aud|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=(sil)",
            "syncmap": "output/sonnet.sil.aud",
            "options": "",
            "show": False,
        },
        "--example-sd": {
            "description": "input: plain text, output: TSV, head/tail detection",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=tsv|is_audio_file_detect_head_max=10.000|is_audio_file_detect_tail_max=10.000",
            "syncmap": "output/sonnet.sd.tsv",
            "options": "",
            "show": False,
        },
        "--example-srt": {
            "description": "input: subtitles text, output: SRT",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/subtitles.txt", __file__),
            "config": "task_language=eng|is_text_type=subtitles|os_task_file_format=srt",
            "syncmap": "output/sonnet.srt",
            "options": "",
            "show": True,
        },
        "--example-smil": {
            "description": "input: unparsed text, output: SMIL",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/page.xhtml", __file__),
            "config": "task_language=eng|is_text_type=unparsed|is_text_unparsed_id_regex=f[0-9]+|is_text_unparsed_id_sort=numeric|os_task_file_format=smil|os_task_file_smil_audio_ref=p001.mp3|os_task_file_smil_page_ref=p001.xhtml",
            "syncmap": "output/sonnet.smil",
            "options": "",
            "show": True,
        },
        "--example-textgrid": {
            "description": "input: parsed text, output: TextGrid",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/parsed.txt", __file__),
            "config": "task_language=eng|is_text_type=parsed|os_task_file_format=textgrid",
            "syncmap": "output/sonnet.textgrid",
            "options": "",
            "show": True,
        },
        "--example-tsv": {
            "description": "input: parsed text, output: TSV",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/parsed.txt", __file__),
            "config": "task_language=eng|is_text_type=parsed|os_task_file_format=tsv",
            "syncmap": "output/sonnet.tsv",
            "options": "",
            "show": True,
        },
        "--example-words": {
            "description": "input: single word granularity plain text, output: AUD",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/words.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=aud",
            "syncmap": "output/sonnet.words.aud",
            "options": "",
            "show": True,
        },
        "--example-words-multilevel": {
            "description": "input: mplain text (multilevel), output: AUD, levels to output: 3",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/mplain.txt", __file__),
            "config": "task_language=eng|is_text_type=mplain|os_task_file_format=aud|os_task_file_levels=3",
            "syncmap": "output/sonnet.words.multilevel.aud",
            "options": "",
            "show": False,
        },
        "--example-words-festival-cache": {
            "description": "input: single word granularity plain text, output: AUD, tts engine: Festival, TTS cache on",
            "audio": AUDIO_FILE,
            "text": gf.relative_path("res/words.txt", __file__),
            "config": "task_language=eng-USA|is_text_type=plain|os_task_file_format=aud",
            "syncmap": "output/sonnet.words.aud",
            "options": '-r="tts=festival|tts_cache=True"',
            "show": False,
        },
        "--example-youtube": {
            "description": "input: audio from YouTube, output: TXT",
            "audio": "https://www.youtube.com/watch?v=rU4a7AA8wM0",
            "text": gf.relative_path("res/plain.txt", __file__),
            "config": "task_language=eng|is_text_type=plain|os_task_file_format=txt",
            "syncmap": "output/sonnet.txt",
            "options": "-y",
            "show": True,
        },
    }

    PARAMETERS = TaskConfiguration.parameters(sort=True, as_strings=True)

    VALUES = {
        "aws": AWSTTSWrapper.CODE_TO_HUMAN_LIST,
        "espeak": ESPEAKTTSWrapper.CODE_TO_HUMAN_LIST,
        "espeak-ng": ESPEAKNGTTSWrapper.CODE_TO_HUMAN_LIST,
        "festival": FESTIVALTTSWrapper.CODE_TO_HUMAN_LIST,
        "macos": MacOSTTSWrapper.CODE_TO_HUMAN_LIST,
        "nuance": NuanceTTSWrapper.CODE_TO_HUMAN_LIST,
        "task_language": Language.CODE_TO_HUMAN_LIST,
        "is_text_type": TextFileFormat.ALLOWED_VALUES,
        "is_text_unparsed_id_sort": IDSortingAlgorithm.ALLOWED_VALUES,
        "os_task_file_format": SyncMapFormat.ALLOWED_VALUES,
        "os_task_file_head_tail_format": SyncMapHeadTailFormat.ALLOWED_VALUES,
        "task_adjust_boundary_algorithm": AdjustBoundaryAlgorithm.ALLOWED_VALUES,
    }

    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Execute a Task.",
        "synopsis": [
            ("--list-parameters", False),
            ("--list-values[=PARAM]", False),
            ("AUDIO_FILE  TEXT_FILE CONFIG_STRING OUTPUT_FILE", True),
            ("YOUTUBE_URL TEXT_FILE CONFIG_STRING OUTPUT_FILE -y", True),
        ],
        "examples": ["--examples", "--examples-all"],
        "options": [
            "--faster-rate : print fragments with rate > task_adjust_boundary_rate_value",
            "--keep-audio : do not delete the audio file downloaded from YouTube (-y only)",
            "--largest-audio : download largest audio stream (-y only)",
            "--list-parameters : list all parameters",
            "--list-values : list all parameters for which values can be listed",
            "--list-values=PARAM : list all allowed values for parameter PARAM",
            "--output-html : output HTML file for fine tuning",
            "--presets-word : apply presets for word-level alignment (MFCC masking)",
            "--rate : print rate of each fragment",
            "--skip-validator : do not validate the given config string",
            "--zero : print fragments with zero duration",
            "-y, --youtube : download audio from YouTube video",
        ],
        "parameters": [],
    }

    def perform_command(self):
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """
        if len(self.actual_arguments) < 1:
            return self.print_help()

        if self.has_option(["-e", "--examples"]):
            return self.print_examples(False)

        if self.has_option("--examples-all"):
            return self.print_examples(True)

        if self.has_option(["--list-parameters"]):
            return self.print_parameters()

        parameter = self.has_option_with_value("--list-values")
        if parameter is not None:
            return self.print_values(parameter)
        elif self.has_option("--list-values"):
            return self.print_values("?")

        # NOTE list() is needed for Python3, where keys() is not a list!
        demo = self.has_option(list(self.DEMOS.keys()))
        demo_parameters = ""
        download_from_youtube = self.has_option(["-y", "--youtube"])
        largest_audio = self.has_option("--largest-audio")
        keep_audio = self.has_option("--keep-audio")
        output_html = self.has_option("--output-html")
        validate = not self.has_option("--skip-validator")
        print_faster_rate = self.has_option("--faster-rate")
        print_rates = self.has_option("--rate")
        print_zero = self.has_option("--zero")
        presets_word = self.has_option("--presets-word")

        if demo:
            validate = False
            for key in self.DEMOS:
                if self.has_option(key):
                    demo_parameters = self.DEMOS[key]
                    audio_file_path = demo_parameters["audio"]
                    text_file_path = demo_parameters["text"]
                    config_string = demo_parameters["config"]
                    sync_map_file_path = demo_parameters["syncmap"]
                    # TODO allow injecting rconf options directly from DEMOS options field
                    if key == "--example-cewsubprocess":
                        self.rconf[RuntimeConfiguration.CEW_SUBPROCESS_ENABLED] = True
                    elif key == "--example-ctw-espeak":
                        self.rconf[RuntimeConfiguration.TTS] = "custom"
                        self.rconf[RuntimeConfiguration.TTS_PATH] = self.CTW_ESPEAK
                    elif key == "--example-ctw-speect":
                        self.rconf[RuntimeConfiguration.TTS] = "custom"
                        self.rconf[RuntimeConfiguration.TTS_PATH] = self.CTW_SPEECT
                    elif key == "--example-festival":
                        self.rconf[RuntimeConfiguration.TTS] = "festival"
                    elif key == "--example-mws":
                        self.rconf[RuntimeConfiguration.MFCC_WINDOW_LENGTH] = "1.500"
                        self.rconf[RuntimeConfiguration.MFCC_WINDOW_SHIFT] = "0.500"
                    elif key == "--example-multilevel-tts":
                        self.rconf[RuntimeConfiguration.TTS_L1] = "festival"
                        self.rconf[RuntimeConfiguration.TTS_L2] = "festival"
                        self.rconf[RuntimeConfiguration.TTS_L3] = "espeak"
                    elif key == "--example-words-festival-cache":
                        self.rconf[RuntimeConfiguration.TTS] = "festival"
                        self.rconf[RuntimeConfiguration.TTS_CACHE] = True
                    elif key == "--example-faster-rate":
                        print_faster_rate = True
                    elif key == "--example-no-zero":
                        print_zero = True
                    elif key == "--example-py":
                        self.rconf[RuntimeConfiguration.C_EXTENSIONS] = False
                    elif key == "--example-rate":
                        print_rates = True
                    elif key == "--example-remove-nonspeech-rateaggressive":
                        print_rates = True
                    elif key == "--example-youtube":
                        download_from_youtube = True
                    break
        else:
            if len(self.actual_arguments) < 4:
                return self.print_help()
            audio_file_path = self.actual_arguments[0]
            text_file_path = self.actual_arguments[1]
            config_string = self.actual_arguments[2]
            sync_map_file_path = self.actual_arguments[3]

        if presets_word:
            self.print_info("Preset for word-level alignment")
            self.rconf[RuntimeConfiguration.MFCC_MASK_NONSPEECH] = True
            self.rconf[RuntimeConfiguration.MFCC_MASK_NONSPEECH_L3] = True

        html_file_path = None
        if output_html:
            keep_audio = True
            html_file_path = sync_map_file_path + ".html"

        if download_from_youtube:
            youtube_url = gf.safe_unicode(audio_file_path)

        if (not download_from_youtube) and (not self.check_input_file(audio_file_path)):
            return self.ERROR_EXIT_CODE
        if not self.check_input_file(text_file_path):
            return self.ERROR_EXIT_CODE
        if not self.check_output_file(sync_map_file_path):
            return self.ERROR_EXIT_CODE
        if (html_file_path is not None) and (
            not self.check_output_file(html_file_path)
        ):
            return self.ERROR_EXIT_CODE

        self.check_c_extensions()

        if demo:
            msg = []
            msg.append("Running example task with arguments:")
            if download_from_youtube:
                msg.append("  YouTube URL:   %s" % youtube_url)
            else:
                msg.append("  Audio file:    %s" % audio_file_path)
            msg.append("  Text file:     %s" % text_file_path)
            msg.append("  Config string: %s" % config_string)
            msg.append("  Sync map file: %s" % sync_map_file_path)
            if len(demo_parameters["options"]) > 0:
                msg.append("  Options:       %s" % demo_parameters["options"])
            self.print_info("\n".join(msg))

        if validate:
            self.print_info(
                "Validating config string (specify --skip-validator to bypass)..."
            )
            validator = Validator(logger=self.logger)
            result = validator.check_configuration_string(
                config_string, is_job=False, external_name=True
            )
            if not result.passed:
                self.print_error("The given config string is not valid:")
                self.print_generic(result.pretty_print())
                return self.ERROR_EXIT_CODE
            self.print_info("Validating config string... done")

        if download_from_youtube:
            try:
                self.print_info("Downloading audio from '%s' ..." % youtube_url)
                downloader = Downloader(logger=self.logger)
                audio_file_path = downloader.audio_from_youtube(
                    youtube_url,
                    download=True,
                    output_file_path=None,
                    largest_audio=largest_audio,
                )
                self.print_info("Downloading audio from '%s' ... done" % youtube_url)
            except ImportError:
                self.print_no_dependency_error()
                return self.ERROR_EXIT_CODE
            except Exception as exc:
                self.print_error(
                    "An unexpected error occurred while downloading audio from YouTube:"
                )
                self.print_error("%s" % exc)
                return self.ERROR_EXIT_CODE
        else:
            audio_extension = gf.file_extension(audio_file_path)
            if audio_extension.lower() not in AudioFile.FILE_EXTENSIONS:
                self.print_warning(
                    "Your audio file path has extension '%s', which is uncommon for an audio file."
                    % audio_extension
                )
                self.print_warning("Attempting at executing your Task anyway.")
                self.print_warning(
                    "If it fails, you might have swapped the first two arguments."
                )
                self.print_warning(
                    "The audio file path should be the first argument, the text file path the second."
                )

        try:
            self.print_info("Creating task...")
            task = Task(config_string, logger=self.logger)
            task.audio_file_path_absolute = audio_file_path
            task.text_file_path_absolute = text_file_path
            task.sync_map_file_path_absolute = sync_map_file_path
            self.print_info("Creating task... done")
        except Exception as exc:
            self.print_error("An unexpected error occurred while creating the task:")
            self.print_error("%s" % exc)
            return self.ERROR_EXIT_CODE

        try:
            self.print_info("Executing task...")
            executor = ExecuteTask(task=task, rconf=self.rconf, logger=self.logger)
            executor.execute()
            self.print_info("Executing task... done")
        except Exception as exc:
            self.print_error("An unexpected error occurred while executing the task:")
            self.print_error("%s" % exc)
            return self.ERROR_EXIT_CODE

        try:
            self.print_info("Creating output sync map file...")
            path = task.output_sync_map_file()
            self.print_info("Creating output sync map file... done")
            self.print_success("Created file '%s'" % path)
        except Exception as exc:
            self.print_error(
                "An unexpected error occurred while writing the sync map file:"
            )
            self.print_error("%s" % exc)
            return self.ERROR_EXIT_CODE

        if output_html:
            try:
                parameters = {}
                parameters[gc.PPN_TASK_OS_FILE_FORMAT] = task.configuration["o_format"]
                parameters[gc.PPN_TASK_OS_FILE_EAF_AUDIO_REF] = task.configuration[
                    "o_eaf_audio_ref"
                ]
                parameters[gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF] = task.configuration[
                    "o_smil_audio_ref"
                ]
                parameters[gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF] = task.configuration[
                    "o_smil_page_ref"
                ]
                self.print_info("Creating output HTML file...")
                task.sync_map.output_html_for_tuning(
                    audio_file_path, html_file_path, parameters
                )
                self.print_info("Creating output HTML file... done")
                self.print_success("Created file '%s'" % html_file_path)
            except Exception as exc:
                self.print_error(
                    "An unexpected error occurred while writing the HTML file:"
                )
                self.print_error("%s" % exc)
                return self.ERROR_EXIT_CODE

        if download_from_youtube:
            if keep_audio:
                self.print_info(
                    "Option --keep-audio set: keeping downloaded file '%s'"
                    % audio_file_path
                )
            else:
                gf.delete_file(None, audio_file_path)

        if print_zero:
            zero_duration = [
                leaf
                for leaf in task.sync_map_leaves(SyncMapFragment.REGULAR)
                if leaf.begin == leaf.end
            ]
            if len(zero_duration) > 0:
                self.print_warning("Fragments with zero duration:")
                for fragment in zero_duration:
                    self.print_generic("  %s" % (fragment.pretty_print))

        if print_rates:
            self.print_info("Fragments with rates:")
            for fragment in task.sync_map_leaves(SyncMapFragment.REGULAR):
                self.print_generic(
                    f"  {fragment.pretty_print}\t{fragment.rate or 0.0:.3f}"
                )

        if print_faster_rate:
            max_rate = task.configuration["aba_rate_value"]
            if max_rate is not None:
                faster = [
                    leaf
                    for leaf in task.sync_map_leaves(SyncMapFragment.REGULAR)
                    if leaf.rate >= max_rate + Decimal("0.001")
                ]
                if len(faster) > 0:
                    self.print_warning(
                        "Fragments with rate greater than %.3f:" % max_rate
                    )
                    for fragment in faster:
                        self.print_generic(
                            "  {}\t{:.3f}".format(
                                fragment.pretty_print, fragment.rate or 0.0
                            )
                        )

        return self.NO_ERROR_EXIT_CODE

    def print_examples(self, full=False):
        """
        Print the examples and exit.

        :param bool full: if ``True``, print all examples; otherwise,
                          print only selected ones
        """
        msg = []
        i = 1
        for key in sorted(self.DEMOS.keys()):
            example = self.DEMOS[key]
            if full or example["show"]:
                msg.append("Example %d (%s)" % (i, example["description"]))
                msg.append(f"  $ {self.invoke} {key}")
                msg.append("")
                i += 1
        self.print_generic("\n" + "\n".join(msg) + "\n")
        return self.HELP_EXIT_CODE

    def print_parameters(self):
        """
        Print the list of parameters and exit.
        """
        self.print_info("You can use --list-values=PARAM on parameters marked by '*'")
        self.print_info("Parameters marked by 'REQ' are required")
        self.print_info("Available parameters:")
        self.print_generic("\n" + "\n".join(self.PARAMETERS) + "\n")
        return self.HELP_EXIT_CODE

    def print_values(self, parameter):
        """
        Print the list of values for the given parameter and exit.

        If ``parameter`` is invalid, print the list of
        parameter names that have allowed values.

        :param parameter: the parameter name
        :type  parameter: Unicode string
        """
        if parameter in self.VALUES:
            self.print_info("Available values for parameter '%s':" % parameter)
            self.print_generic("\n".join(self.VALUES[parameter]))
            return self.HELP_EXIT_CODE
        if parameter not in ["?", ""]:
            self.print_error("Invalid parameter name '%s'" % parameter)
        self.print_info("Parameters for which values can be listed:")
        self.print_generic("\n".join(sorted(self.VALUES.keys())))
        return self.HELP_EXIT_CODE


def main():
    """
    Execute program.
    """
    ExecuteTaskCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
