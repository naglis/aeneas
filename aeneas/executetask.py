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

import logging
import tempfile

from aeneas.adjustboundaryalgorithm import AdjustBoundaryAlgorithm
from aeneas.audiofile import AudioFile
from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.dtw import DTWAligner
from aeneas.exacttiming import TimeValue
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.sd import SD
from aeneas.syncmap import SyncMap
from aeneas.synthesizer import Synthesizer
from aeneas.task import Task
from aeneas.textfile import TextFileFormat, TextFile
from aeneas.tree import Tree
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class ExecuteTaskExecutionError(Exception):
    """
    Error raised when the execution of the task fails for internal reasons.
    """


class ExecuteTaskInputError(Exception):
    """
    Error raised when the input parameters of the task are invalid or missing.
    """


class ExecuteTask(Configurable):
    """
    Execute a task, that is, compute the sync map for it.

    :param task: the task to be executed
    :type  task: :class:`~aeneas.task.Task`
    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    def __init__(self, task: Task, rconf=None):
        super().__init__(rconf=rconf)
        self.task = task
        self.step_index = 1
        self.step_label = ""
        self.synthesizer = Synthesizer.from_rconf(self.rconf)

    def _step_begin(self, label, log: bool = True):
        """Log begin of a step"""
        if log:
            self.step_label = label
            logger.debug("STEP %d BEGIN (%s)", self.step_index, label)

    def _step_end(self, log: bool = True):
        """Log end of a step"""
        if log:
            logger.debug("STEP %d END (%s)", self.step_index, self.step_label)
            self.step_index += 1

    def _step_failure(self, exc):
        """Log failure of a step"""
        logger.critical("STEP %d (%s) FAILURE", self.step_index, self.step_label)
        self.step_index += 1
        raise ExecuteTaskExecutionError(
            "Unexpected error while executing task"
        ) from exc

    def execute(self):
        """
        Execute the task.
        The sync map produced will be stored inside the task object.

        :raises: :class:`~aeneas.executetask.ExecuteTaskInputError`: if there is a problem with the input parameters
        :raises: :class:`~aeneas.executetask.ExecuteTaskExecutionError`: if there is a problem during the task execution
        """
        logger.debug("Executing task...")

        # check that we have the AudioFile object
        if self.task.audio_file is None:
            raise ExecuteTaskInputError(
                "The task does not seem to have its audio file set"
            )
        if (
            self.task.audio_file.audio_length is None
            or self.task.audio_file.audio_length <= 0
        ):
            raise ExecuteTaskInputError("The task seems to have an invalid audio file")
        task_max_audio_length = self.rconf[RuntimeConfiguration.TASK_MAX_AUDIO_LENGTH]
        if (
            task_max_audio_length > 0
            and self.task.audio_file.audio_length > task_max_audio_length
        ):
            raise ExecuteTaskInputError(
                f"The audio file of the task has length {self.task.audio_file.audio_length:.3f}, "
                f"more than the maximum allowed ({task_max_audio_length:.3f})."
            )

        # check that we have the TextFile object
        if self.task.text_file is None:
            raise ExecuteTaskInputError(
                "The task does not seem to have its text file set"
            )
        if len(self.task.text_file) == 0:
            raise ExecuteTaskInputError(
                "The task text file seems to have no text fragments"
            )
        task_max_text_length = self.rconf[RuntimeConfiguration.TASK_MAX_TEXT_LENGTH]
        if task_max_text_length > 0 and len(self.task.text_file) > task_max_text_length:
            raise ExecuteTaskInputError(
                f"The text file of the task has {len(self.task.text_file):d} fragments, "
                f"more than the maximum allowed ({task_max_text_length:d})."
            )
        if self.task.text_file.chars == 0:
            raise ExecuteTaskInputError("The task text file seems to have empty text")

        logger.debug("Both audio and text input file are present")

        # execute
        self.step_index = 1
        if self.task.configuration[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] in TextFileFormat.MULTILEVEL_VALUES:
            self._execute_multi_level_task()
        else:
            self._execute_single_level_task()
        logger.debug("Executing task... done")

    def _execute_single_level_task(self):
        """Execute a single-level task"""
        logger.debug("Executing single level task...")
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

            logger.debug("Executing single level task... done")
        except Exception as exc:
            logger.exception("An error occurred while executing single level task")
            self._step_failure(exc)

    def _execute_multi_level_task(self):
        """Execute a multi-level task"""
        logger.debug("Executing multi level task...")

        logger.debug("Saving rconf...")
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
            logger.debug("Level %d mmn: %s", i, level_rconfs[i].mmn)
            logger.debug("Level %d mwl: %.3f", i, level_rconfs[i].mwl)
            logger.debug("Level %d mws: %.3f", i, level_rconfs[i].mws)
            level_rconfs[i].set_tts(i)
            logger.debug("Level %d tts: %s", i, level_rconfs[i].tts)
            logger.debug("Level %d tts_path: %s", i, level_rconfs[i].tts_path)
        logger.debug("Saving rconf... done")
        try:
            logger.debug("Creating AudioFile object...")
            audio_file = self._load_audio_file()
            logger.debug("Creating AudioFile object... done")

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
                    logger.debug("Keeping MFCC real wave from previous level")
                    level_mfccs[i] = level_mfccs[i - 1]
                self._step_end()

            logger.debug("Clearing AudioFile object...")
            self.rconf = level_rconfs[1]
            self._clear_audio_file(audio_file)
            logger.debug("Clearing AudioFile object... done")

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

            logger.debug("Executing multi level task... done")
        except Exception as exc:
            self._step_failure(exc)

    def _execute_level(
        self,
        level: int,
        audio_file_mfcc: AudioFileMFCC,
        text_files: list[TextFile],
        sync_roots: list[Tree],
        force_aba_auto: bool = False,
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
        next_level_text_files = []
        next_level_sync_roots = []
        for text_file_index, text_file in enumerate(text_files):
            logger.debug(
                "Text level: %d, fragment: %d, len: %d",
                level,
                text_file_index,
                len(text_file),
            )
            sync_root = sync_roots[text_file_index]
            if level > 1 and len(text_file) == 1:
                logger.debug(
                    "Level > 1 and only one text fragment => return trivial tree"
                )
                self._append_trivial_tree(text_file, sync_root)
            elif level > 1 and sync_root.value.begin == sync_root.value.end:
                logger.debug(
                    "Level > 1 and parent has begin == end => return trivial tree"
                )
                self._append_trivial_tree(text_file, sync_root)
            else:
                logger.debug(
                    "Level == 1 or more than one text fragment with non-zero parent => compute tree"
                )
                if not sync_root.is_empty:
                    begin = sync_root.value.begin
                    end = sync_root.value.end
                    logger.debug("Setting begin: %.3f", begin)
                    logger.debug("Setting end: %.3f", end)
                    audio_file_mfcc.set_head_middle_tail(
                        head_length=begin, middle_length=(end - begin)
                    )
                else:
                    logger.debug("No begin or end to set")
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
        audio_file_mfcc: AudioFileMFCC,
        text_file: TextFile,
        sync_root: Tree,
        force_aba_auto: bool = False,
        log: bool = True,
        leaf_level: bool = False,
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

    def _load_audio_file(self) -> AudioFile:
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
        )
        audio_file.read_samples_from_file()
        self._step_end()
        return audio_file

    def _clear_audio_file(self, audio_file: AudioFile):
        """
        Clear audio from memory.

        :param audio_file: the object to clear
        :type  audio_file: :class:`~aeneas.audiofile.AudioFile`
        """
        self._step_begin("clear audio file")
        audio_file.clear_data()
        self._step_end()

    def _extract_mfcc(
        self, file_path=None, file_format=None, audio_file=None
    ) -> AudioFileMFCC:
        """
        Extract the MFCCs from the given audio file.

        :rtype: :class:`~aeneas.audiofilemfcc.AudioFileMFCC`
        """
        audio_file_mfcc = AudioFileMFCC(
            file_path=file_path,
            file_format=file_format,
            audio_file=audio_file,
            rconf=self.rconf,
        )
        if self.rconf.mmn:
            logger.debug("Running VAD inside _extract_mfcc...")
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
            logger.debug("Running VAD inside _extract_mfcc... done")
        return audio_file_mfcc

    def _compute_head_process_tail(self, audio_file_mfcc: AudioFileMFCC):
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
            head_length is not None
            or process_length is not None
            or tail_length is not None
        ):
            logger.debug("Setting explicit head process tail")
        else:
            logger.debug("Detecting head tail...")
            sd = SD(
                audio_file_mfcc,
                self.task.text_file,
                rconf=self.rconf,
            )
            head_length = TimeValue("0.000")
            process_length = None
            tail_length = TimeValue("0.000")
            if head_min is not None or head_max is not None:
                logger.debug("Detecting HEAD...")
                head_length = sd.detect_head(head_min, head_max)
                logger.debug("Detected HEAD: %.3f", head_length)
                logger.debug("Detecting HEAD... done")
            if tail_min is not None or tail_max is not None:
                logger.debug("Detecting TAIL...")
                tail_length = sd.detect_tail(tail_min, tail_max)
                logger.debug("Detected TAIL: %.3f", tail_length)
                logger.debug("Detecting TAIL... done")
            logger.debug("Detecting head tail... done")
        logger.debug("Head:    %s", gf.safe_float(head_length, None))
        logger.debug("Process: %s", gf.safe_float(process_length, None))
        logger.debug("Tail:    %s", gf.safe_float(tail_length, None))
        return (head_length, process_length, tail_length)

    def _clear_cache_synthesizer(self):
        """Clear the cache of the synthesizer"""
        self.synthesizer.clear_cache()

    def _synthesize(self, text_file: TextFile, output_path: str) -> tuple[str, list]:
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
        logger.debug("Creating DTWAligner...")
        aligner = DTWAligner(real_wave_mfcc, synt_wave_mfcc, rconf=self.rconf)
        logger.debug("Creating DTWAligner... done")
        logger.debug("Computing boundary indices...")
        boundary_indices = aligner.compute_boundaries(synt_anchors)
        logger.debug("Computing boundary indices... done")
        return boundary_indices

    def _adjust_boundaries(
        self,
        boundary_indices,
        text_file: TextFile,
        real_wave_mfcc,
        sync_root: Tree,
        force_aba_auto: bool = False,
        leaf_level: bool = False,
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
            logger.debug("Forced running algorithm: 'auto'")
            aba_parameters["algorithm"] = (AdjustBoundaryAlgorithm.AUTO, [])
            # note that the other aba settings (nonspeech and nozero)
            # remain as specified by the user
        logger.debug("ABA parameters: %s", aba_parameters)
        aba = AdjustBoundaryAlgorithm(rconf=self.rconf)
        aba.adjust(
            aba_parameters=aba_parameters,
            real_wave_mfcc=real_wave_mfcc,
            boundary_indices=boundary_indices,
            text_file=text_file,
            allow_arbitrary_shift=leaf_level,
        )
        aba.append_fragment_list_to_sync_root(sync_root=sync_root)

    def _append_trivial_tree(self, text_file: TextFile, sync_root: Tree):
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
        aba = AdjustBoundaryAlgorithm(rconf=self.rconf)
        aba.intervals_to_fragment_list(text_file=text_file, time_values=time_values)
        aba.append_fragment_list_to_sync_root(sync_root=sync_root)

    def _create_sync_map(self, sync_root: Tree):
        """
        If requested, check that the computed sync map is consistent.
        Then, add it to the Task.
        """
        sync_map = SyncMap(tree=sync_root)
        if self.rconf.safety_checks:
            logger.debug("Running sanity check on computed sync map...")
            if not sync_map.leaves_are_consistent:
                self._step_failure(
                    ValueError("The computed sync map contains inconsistent fragments")
                )
            logger.debug("Running sanity check on computed sync map... passed")
        else:
            logger.debug("Not running sanity check on computed sync map")
        self.task.sync_map = sync_map
