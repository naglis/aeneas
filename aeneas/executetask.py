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

* :class:`~aeneas.executetask.ExecuteTask`, a class to process a task;
* :class:`~aeneas.executetask.ExecuteTaskExecutionError`, and
* :class:`~aeneas.executetask.ExecuteTaskInputError`,
  representing errors generated while processing tasks.
"""

import tempfile

from aeneas.adjustboundaryalgorithm import AdjustBoundaryAlgorithm
from aeneas.audiofile import AudioFile
from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.dtw import DTWAligner
from aeneas.exacttiming import TimeValue
from aeneas.logger import Loggable
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.sd import SD
from aeneas.syncmap import SyncMap
from aeneas.synthesizer import Synthesizer
from aeneas.task import Task
from aeneas.textfile import TextFileFormat, TextFile
from aeneas.tree import Tree
import aeneas.globalfunctions as gf


class ExecuteTaskExecutionError(Exception):
    """
    Error raised when the execution of the task fails for internal reasons.
    """

    pass


class ExecuteTaskInputError(Exception):
    """
    Error raised when the input parameters of the task are invalid or missing.
    """

    pass


class ExecuteTask(Loggable):
    """
    Execute a task, that is, compute the sync map for it.

    :param task: the task to be executed
    :type  task: :class:`~aeneas.task.Task`
    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :param logger: the logger object
    :type  logger: :class:`~aeneas.logger.Logger`
    """

    TAG = "ExecuteTask"

    def __init__(self, task=None, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)
        self.task = task
        self.step_index = 1
        self.step_label = ""
        self.step_begin_time = None
        self.step_total = 0.000
        self.synthesizer = None
        if task is not None:
            self.load_task(self.task)

    def load_task(self, task):
        """
        Load the task from the given ``Task`` object.

        :param task: the task to load
        :type  task: :class:`~aeneas.task.Task`
        :raises: :class:`~aeneas.executetask.ExecuteTaskInputError`: if ``task`` is not an instance of :class:`~aeneas.task.Task`
        """
        if not isinstance(task, Task):
            self.log_exc(
                "task is not an instance of Task", None, True, ExecuteTaskInputError
            )
        self.task = task

    def _step_begin(self, label, log=True):
        """Log begin of a step"""
        if log:
            self.step_label = label
            self.step_begin_time = self.log(
                "STEP %d BEGIN (%s)" % (self.step_index, label)
            )

    def _step_end(self, log=True):
        """Log end of a step"""
        if log:
            step_end_time = self.log(
                "STEP %d END (%s)" % (self.step_index, self.step_label)
            )
            diff = step_end_time - self.step_begin_time
            diff = float(diff.seconds + diff.microseconds / 1000000.0)
            self.step_total += diff
            self.log(
                "STEP %d DURATION %.3f (%s)" % (self.step_index, diff, self.step_label)
            )
            self.step_index += 1

    def _step_failure(self, exc):
        """Log failure of a step"""
        self.log_crit("STEP %d (%s) FAILURE" % (self.step_index, self.step_label))
        self.step_index += 1
        self.log_exc(
            "Unexpected error while executing task",
            exc,
            True,
            ExecuteTaskExecutionError,
        )

    def _step_total(self):
        """Log total"""
        self.log("STEP T DURATION %.3f" % (self.step_total))

    def execute(self):
        """
        Execute the task.
        The sync map produced will be stored inside the task object.

        :raises: :class:`~aeneas.executetask.ExecuteTaskInputError`: if there is a problem with the input parameters
        :raises: :class:`~aeneas.executetask.ExecuteTaskExecutionError`: if there is a problem during the task execution
        """
        self.log("Executing task...")

        # check that we have the AudioFile object
        if self.task.audio_file is None:
            self.log_exc(
                "The task does not seem to have its audio file set",
                None,
                True,
                ExecuteTaskInputError,
            )
        if (self.task.audio_file.audio_length is None) or (
            self.task.audio_file.audio_length <= 0
        ):
            self.log_exc(
                "The task seems to have an invalid audio file",
                None,
                True,
                ExecuteTaskInputError,
            )
        task_max_audio_length = self.rconf[RuntimeConfiguration.TASK_MAX_AUDIO_LENGTH]
        if (task_max_audio_length > 0) and (
            self.task.audio_file.audio_length > task_max_audio_length
        ):
            self.log_exc(
                "The audio file of the task has length {:.3f}, more than the maximum allowed ({:.3f}).".format(
                    self.task.audio_file.audio_length, task_max_audio_length
                ),
                None,
                True,
                ExecuteTaskInputError,
            )

        # check that we have the TextFile object
        if self.task.text_file is None:
            self.log_exc(
                "The task does not seem to have its text file set",
                None,
                True,
                ExecuteTaskInputError,
            )
        if len(self.task.text_file) == 0:
            self.log_exc(
                "The task text file seems to have no text fragments",
                None,
                True,
                ExecuteTaskInputError,
            )
        task_max_text_length = self.rconf[RuntimeConfiguration.TASK_MAX_TEXT_LENGTH]
        if (task_max_text_length > 0) and (
            len(self.task.text_file) > task_max_text_length
        ):
            self.log_exc(
                "The text file of the task has %d fragments, more than the maximum allowed (%d)."
                % (len(self.task.text_file), task_max_text_length),
                None,
                True,
                ExecuteTaskInputError,
            )
        if self.task.text_file.chars == 0:
            self.log_exc(
                "The task text file seems to have empty text",
                None,
                True,
                ExecuteTaskInputError,
            )

        self.log("Both audio and text input file are present")

        # execute
        self.step_index = 1
        self.step_total = 0.000
        if self.task.text_file.file_format in TextFileFormat.MULTILEVEL_VALUES:
            self._execute_multi_level_task()
        else:
            self._execute_single_level_task()
        self.log("Executing task... done")

    def _execute_single_level_task(self):
        """Execute a single-level task"""
        self.log("Executing single level task...")
        try:
            # load audio file, extract MFCCs from real wave, clear audio file
            self._step_begin("extract MFCC real wave")
            real_wave_mfcc = self._extract_mfcc(
                file_path=self.task.audio_file_path_absolute,
                file_format=None,
            )
            self._step_end()

            # compute head and/or tail and set it
            self._step_begin("compute head tail")
            (head_length, process_length, tail_length) = (
                self._compute_head_process_tail(real_wave_mfcc)
            )
            real_wave_mfcc.set_head_middle_tail(
                head_length, process_length, tail_length
            )
            self._step_end()

            # compute alignment, outputting a tree of time intervals
            self._set_synthesizer()
            sync_root = Tree()
            self._execute_inner(
                real_wave_mfcc,
                self.task.text_file,
                sync_root=sync_root,
                force_aba_auto=False,
                log=True,
                leaf_level=True,
            )
            self._clear_cache_synthesizer()

            # create syncmap and add it to task
            self._step_begin("create sync map")
            self._create_sync_map(sync_root=sync_root)
            self._step_end()

            # log total
            self._step_total()
            self.log("Executing single level task... done")
        except Exception as exc:
            self._step_failure(exc)

    def _execute_multi_level_task(self):
        """Execute a multi-level task"""
        self.log("Executing multi level task...")

        self.log("Saving rconf...")
        # save original rconf
        orig_rconf = self.rconf.clone()
        # clone rconfs and set granularity
        # TODO the following code assumes 3 levels: generalize this
        level_rconfs = [
            None,
            self.rconf.clone(),
            self.rconf.clone(),
            self.rconf.clone(),
        ]
        level_mfccs = [None, None, None, None]
        force_aba_autos = [None, False, False, True]
        for i in range(1, len(level_rconfs)):
            level_rconfs[i].set_granularity(i)
            self.log(["Level %d mmn: %s", i, level_rconfs[i].mmn])
            self.log(["Level %d mwl: %.3f", i, level_rconfs[i].mwl])
            self.log(["Level %d mws: %.3f", i, level_rconfs[i].mws])
            level_rconfs[i].set_tts(i)
            self.log(["Level %d tts: %s", i, level_rconfs[i].tts])
            self.log(["Level %d tts_path: %s", i, level_rconfs[i].tts_path])
        self.log("Saving rconf... done")
        try:
            self.log("Creating AudioFile object...")
            audio_file = self._load_audio_file()
            self.log("Creating AudioFile object... done")

            # extract MFCC for each level
            for i in range(1, len(level_rconfs)):
                self._step_begin("extract MFCC real wave level %d" % i)
                if (
                    (i == 1)
                    or (level_rconfs[i].mws != level_rconfs[i - 1].mws)
                    or (level_rconfs[i].mwl != level_rconfs[i - 1].mwl)
                ):
                    self.rconf = level_rconfs[i]
                    level_mfccs[i] = self._extract_mfcc(audio_file=audio_file)
                else:
                    self.log("Keeping MFCC real wave from previous level")
                    level_mfccs[i] = level_mfccs[i - 1]
                self._step_end()

            self.log("Clearing AudioFile object...")
            self.rconf = level_rconfs[1]
            self._clear_audio_file(audio_file)
            self.log("Clearing AudioFile object... done")

            # compute head tail for the entire real wave (level 1)
            self._step_begin("compute head tail")
            (head_length, process_length, tail_length) = (
                self._compute_head_process_tail(level_mfccs[1])
            )
            level_mfccs[1].set_head_middle_tail(
                head_length, process_length, tail_length
            )
            self._step_end()

            # compute alignment at each level
            sync_root = Tree()
            sync_roots = [sync_root]
            text_files = [self.task.text_file]
            number_levels = len(level_rconfs)
            for i in range(1, number_levels):
                self._step_begin("compute alignment level %d" % i)
                self.rconf = level_rconfs[i]
                text_files, sync_roots = self._execute_level(
                    level=i,
                    audio_file_mfcc=level_mfccs[i],
                    text_files=text_files,
                    sync_roots=sync_roots,
                    force_aba_auto=force_aba_autos[i],
                )
                self._step_end()

            # restore original rconf, and create syncmap and add it to task
            self._step_begin("create sync map")
            self.rconf = orig_rconf
            self._create_sync_map(sync_root=sync_root)
            self._step_end()

            self._step_total()
            self.log("Executing multi level task... done")
        except Exception as exc:
            self._step_failure(exc)

    def _execute_level(
        self, level, audio_file_mfcc, text_files, sync_roots, force_aba_auto=False
    ):
        """
        Compute the alignment for all the nodes in the given level.

        Return a pair (next_level_text_files, next_level_sync_roots),
        containing two lists of text file subtrees and sync map subtrees
        on the next level.

        :param int level: the level
        :param audio_file_mfcc: the audio MFCC representation for this level
        :type  audio_file_mfcc: :class:`~aeneas.audiofilemfcc.AudioFileMFCC`
        :param list text_files: a list of :class:`~aeneas.textfile.TextFile` objects,
                                each representing a (sub)tree of the Task text file
        :param list sync_roots: a list of :class:`~aeneas.tree.Tree` objects,
                                each representing a SyncMapFragment tree,
                                one for each element in ``text_files``
        :param bool force_aba_auto: if ``True``, force using the AUTO ABA algorithm
        :rtype: (list, list)
        """
        self._set_synthesizer()
        next_level_text_files = []
        next_level_sync_roots = []
        for text_file_index, text_file in enumerate(text_files):
            self.log(["Text level %d, fragment %d", level, text_file_index])
            self.log(["  Len:   %d", len(text_file)])
            sync_root = sync_roots[text_file_index]
            if (level > 1) and (len(text_file) == 1):
                self.log("Level > 1 and only one text fragment => return trivial tree")
                self._append_trivial_tree(text_file, sync_root)
            elif (level > 1) and (sync_root.value.begin == sync_root.value.end):
                self.log("Level > 1 and parent has begin == end => return trivial tree")
                self._append_trivial_tree(text_file, sync_root)
            else:
                self.log(
                    "Level == 1 or more than one text fragment with non-zero parent => compute tree"
                )
                if not sync_root.is_empty:
                    begin = sync_root.value.begin
                    end = sync_root.value.end
                    self.log(["  Setting begin: %.3f", begin])
                    self.log(["  Setting end:   %.3f", end])
                    audio_file_mfcc.set_head_middle_tail(
                        head_length=begin, middle_length=(end - begin)
                    )
                else:
                    self.log("  No begin or end to set")
                self._execute_inner(
                    audio_file_mfcc,
                    text_file,
                    sync_root=sync_root,
                    force_aba_auto=force_aba_auto,
                    log=False,
                    leaf_level=(level == 3),
                )
            # store next level roots
            next_level_text_files.extend(text_file.children_not_empty)
            # we added head and tail, we must not pass them to the next level
            next_level_sync_roots.extend(sync_root.children[1:-1])
        self._clear_cache_synthesizer()
        return (next_level_text_files, next_level_sync_roots)

    def _execute_inner(
        self,
        audio_file_mfcc,
        text_file,
        sync_root=None,
        force_aba_auto=False,
        log=True,
        leaf_level=False,
    ):
        """
        Align a subinterval of the given AudioFileMFCC
        with the given TextFile.

        Return the computed tree of time intervals,
        rooted at ``sync_root`` if the latter is not ``None``,
        or as a new ``Tree`` otherwise.

        The begin and end positions inside the AudioFileMFCC
        must have been set ahead by the caller.

        The text fragments being aligned are the vchildren of ``text_file``.

        :param audio_file_mfcc: the audio file MFCC representation
        :type  audio_file_mfcc: :class:`~aeneas.audiofilemfcc.AudioFileMFCC`
        :param text_file: the text file subtree to align
        :type  text_file: :class:`~aeneas.textfile.TextFile`
        :param sync_root: the tree node to which fragments should be appended
        :type  sync_root: :class:`~aeneas.tree.Tree`
        :param bool force_aba_auto: if ``True``, do not run aba algorithm
        :param bool log: if ``True``, log steps
        :param bool leaf_level: alert aba if the computation is at a leaf level
        :rtype: :class:`~aeneas.tree.Tree`
        """

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            dir=self.rconf[RuntimeConfiguration.TMP_PATH],
        ) as tmp_file:
            self._step_begin("synthesize text", log=log)
            synt_anchors, synt_format = self._synthesize(text_file, tmp_file.name)
            self._step_end(log=log)

            self._step_begin("extract MFCC synt wave", log=log)
            synt_wave_mfcc = self._extract_mfcc(
                file_path=tmp_file.name,
                file_format=synt_format,
            )
            self._step_end(log=log)

        self._step_begin("align waves", log=log)
        indices = self._align_waves(audio_file_mfcc, synt_wave_mfcc, synt_anchors)
        self._step_end(log=log)

        self._step_begin("adjust boundaries", log=log)
        self._adjust_boundaries(
            indices, text_file, audio_file_mfcc, sync_root, force_aba_auto, leaf_level
        )
        self._step_end(log=log)

    def _load_audio_file(self):
        """
        Load audio in memory.

        :rtype: :class:`~aeneas.audiofile.AudioFile`
        """
        self._step_begin("load audio file")
        # NOTE file_format=None forces conversion to
        #      PCM16 mono WAVE with default sample rate
        audio_file = AudioFile(
            file_path=self.task.audio_file_path_absolute,
            file_format=None,
            rconf=self.rconf,
            logger=self.logger,
        )
        audio_file.read_samples_from_file()
        self._step_end()
        return audio_file

    def _clear_audio_file(self, audio_file):
        """
        Clear audio from memory.

        :param audio_file: the object to clear
        :type  audio_file: :class:`~aeneas.audiofile.AudioFile`
        """
        self._step_begin("clear audio file")
        audio_file.clear_data()
        audio_file = None
        self._step_end()

    def _extract_mfcc(self, file_path=None, file_format=None, audio_file=None):
        """
        Extract the MFCCs from the given audio file.

        :rtype: :class:`~aeneas.audiofilemfcc.AudioFileMFCC`
        """
        audio_file_mfcc = AudioFileMFCC(
            file_path=file_path,
            file_format=file_format,
            audio_file=audio_file,
            rconf=self.rconf,
            logger=self.logger,
        )
        if self.rconf.mmn:
            self.log("Running VAD inside _extract_mfcc...")
            audio_file_mfcc.run_vad(
                log_energy_threshold=self.rconf[
                    RuntimeConfiguration.MFCC_MASK_LOG_ENERGY_THRESHOLD
                ],
                min_nonspeech_length=self.rconf[
                    RuntimeConfiguration.MFCC_MASK_MIN_NONSPEECH_LENGTH
                ],
                extend_before=self.rconf[
                    RuntimeConfiguration.MFCC_MASK_EXTEND_SPEECH_INTERVAL_BEFORE
                ],
                extend_after=self.rconf[
                    RuntimeConfiguration.MFCC_MASK_EXTEND_SPEECH_INTERVAL_AFTER
                ],
            )
            self.log("Running VAD inside _extract_mfcc... done")
        return audio_file_mfcc

    def _compute_head_process_tail(self, audio_file_mfcc):
        """
        Set the audio file head or tail,
        by either reading the explicit values
        from the Task configuration,
        or using SD to determine them.

        This function returns the lengths, in seconds,
        of the (head, process, tail).

        :rtype: tuple (float, float, float)
        """
        head_length = self.task.configuration["i_a_head"]
        process_length = self.task.configuration["i_a_process"]
        tail_length = self.task.configuration["i_a_tail"]
        head_max = self.task.configuration["i_a_head_max"]
        head_min = self.task.configuration["i_a_head_min"]
        tail_max = self.task.configuration["i_a_tail_max"]
        tail_min = self.task.configuration["i_a_tail_min"]
        if (
            (head_length is not None)
            or (process_length is not None)
            or (tail_length is not None)
        ):
            self.log("Setting explicit head process tail")
        else:
            self.log("Detecting head tail...")
            sd = SD(
                audio_file_mfcc,
                self.task.text_file,
                rconf=self.rconf,
                logger=self.logger,
            )
            head_length = TimeValue("0.000")
            process_length = None
            tail_length = TimeValue("0.000")
            if (head_min is not None) or (head_max is not None):
                self.log("Detecting HEAD...")
                head_length = sd.detect_head(head_min, head_max)
                self.log(["Detected HEAD: %.3f", head_length])
                self.log("Detecting HEAD... done")
            if (tail_min is not None) or (tail_max is not None):
                self.log("Detecting TAIL...")
                tail_length = sd.detect_tail(tail_min, tail_max)
                self.log(["Detected TAIL: %.3f", tail_length])
                self.log("Detecting TAIL... done")
            self.log("Detecting head tail... done")
        self.log(["Head:    %s", gf.safe_float(head_length, None)])
        self.log(["Process: %s", gf.safe_float(process_length, None)])
        self.log(["Tail:    %s", gf.safe_float(tail_length, None)])
        return (head_length, process_length, tail_length)

    def _set_synthesizer(self):
        """Create synthesizer"""
        self.log("Setting synthesizer...")
        self.synthesizer = Synthesizer(rconf=self.rconf, logger=self.logger)
        self.log("Setting synthesizer... done")

    def _clear_cache_synthesizer(self):
        """Clear the cache of the synthesizer"""
        self.log("Clearing synthesizer...")
        self.synthesizer.clear_cache()
        self.log("Clearing synthesizer... done")

    def _synthesize(self, text_file: TextFile, output_path: str):
        """
        Synthesize text into a WAVE file.

        Return a tuple consisting of:

        1. the handler of the generated audio file
        2. the path of the generated audio file
        3. the list of anchors, that is, a list of floats
           each representing the start time of the corresponding
           text fragment in the generated wave file
           ``[start_1, start_2, ..., start_n]``
        4. a tuple describing the format of the audio file

        :param text_file: the text to be synthesized
        :type  text_file: :class:`~aeneas.textfile.TextFile`
        :rtype: tuple (string, list)
        """
        result = self.synthesizer.synthesize(text_file, output_path)
        return (result[0], self.synthesizer.output_audio_format)

    def _align_waves(self, real_wave_mfcc, synt_wave_mfcc, synt_anchors):
        """
        Align two AudioFileMFCC objects,
        representing WAVE files.

        Return a list of boundary indices.
        """
        self.log("Creating DTWAligner...")
        aligner = DTWAligner(
            real_wave_mfcc, synt_wave_mfcc, rconf=self.rconf, logger=self.logger
        )
        self.log("Creating DTWAligner... done")
        self.log("Computing boundary indices...")
        boundary_indices = aligner.compute_boundaries(synt_anchors)
        self.log("Computing boundary indices... done")
        return boundary_indices

    def _adjust_boundaries(
        self,
        boundary_indices,
        text_file,
        real_wave_mfcc,
        sync_root,
        force_aba_auto=False,
        leaf_level=False,
    ):
        """
        Adjust boundaries as requested by the user.

        Return the computed time map, that is,
        a list of pairs ``[start_time, end_time]``,
        of length equal to number of fragments + 2,
        where the two extra elements are for
        the HEAD (first) and TAIL (last).
        """
        # boundary_indices contains the boundary indices in the all_mfcc of real_wave_mfcc
        # starting with the (head-1st fragment) and ending with (-1th fragment-tail)
        aba_parameters = self.task.configuration.aba_parameters()
        if force_aba_auto:
            self.log("Forced running algorithm: 'auto'")
            aba_parameters["algorithm"] = (AdjustBoundaryAlgorithm.AUTO, [])
            # note that the other aba settings (nonspeech and nozero)
            # remain as specified by the user
        self.log(["ABA parameters: %s", aba_parameters])
        aba = AdjustBoundaryAlgorithm(rconf=self.rconf, logger=self.logger)
        aba.adjust(
            aba_parameters=aba_parameters,
            real_wave_mfcc=real_wave_mfcc,
            boundary_indices=boundary_indices,
            text_file=text_file,
            allow_arbitrary_shift=leaf_level,
        )
        aba.append_fragment_list_to_sync_root(sync_root=sync_root)

    def _append_trivial_tree(self, text_file, sync_root):
        """
        Append trivial tree, made by one HEAD,
        one sync map fragment for each element of ``text_file``,
        and one TAIL.

        This function is called if either ``text_file`` has only one element,
        or if ``sync_root.value`` is an interval with zero length
        (i.e., ``sync_root.value.begin == sync_root.value.end``).
        """
        interval = sync_root.value
        #
        # NOTE the following is correct, but it is a bit obscure
        # time_values = [interval.begin] * (1 + len(text_file)) + [interval.end] * 2
        #
        if len(text_file) == 1:
            time_values = [interval.begin, interval.begin, interval.end, interval.end]
        else:
            # interval.begin == interval.end
            time_values = [interval.begin] * (3 + len(text_file))
        aba = AdjustBoundaryAlgorithm(rconf=self.rconf, logger=self.logger)
        aba.intervals_to_fragment_list(text_file=text_file, time_values=time_values)
        aba.append_fragment_list_to_sync_root(sync_root=sync_root)

    def _create_sync_map(self, sync_root):
        """
        If requested, check that the computed sync map is consistent.
        Then, add it to the Task.
        """
        sync_map = SyncMap(tree=sync_root, rconf=self.rconf, logger=self.logger)
        if self.rconf.safety_checks:
            self.log("Running sanity check on computed sync map...")
            if not sync_map.leaves_are_consistent:
                self._step_failure(
                    ValueError("The computed sync map contains inconsistent fragments")
                )
            self.log("Running sanity check on computed sync map... passed")
        else:
            self.log("Not running sanity check on computed sync map")
        self.task.sync_map = sync_map
