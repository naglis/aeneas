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

* :class:`~aeneas.executejob.ExecuteJob`, a class to process a job;
* :class:`~aeneas.executejob.ExecuteJobExecutionError`,
* :class:`~aeneas.executejob.ExecuteJobInputError`, and
* :class:`~aeneas.executejob.ExecuteJobOutputError`,
  representing errors generated while processing jobs.
"""

import logging
import tempfile

from aeneas.analyzecontainer import AnalyzeContainer
from aeneas.container import Container, ContainerFormat
from aeneas.executetask import ExecuteTask
from aeneas.job import Job
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class ExecuteJobExecutionError(Exception):
    """
    Error raised when the execution of the job fails for internal reasons.
    """


class ExecuteJobInputError(Exception):
    """
    Error raised when the input parameters of the job are invalid or missing.
    """


class ExecuteJobOutputError(Exception):
    """
    Error raised when the creation of the output container failed.
    """


class ExecuteJob(Configurable):
    """
    Execute a job, that is, execute all of its tasks
    and generate the output container
    holding the generated sync maps.

    If you do not provide a job object in the constructor,
    you must manually set it later, or load it from a container
    with :func:`~aeneas.executejob.ExecuteJob.load_job_from_container`.

    In the first case, you are responsible for setting
    the absolute audio/text/sync map paths of each task of the job,
    to their actual absolute location on the computing machine.
    Moreover, you are responsible for cleaning up
    any temporary files you might have generated around.

    In the second case, you are responsible for
    calling :func:`~aeneas.executejob.ExecuteJob.clean`
    at the end of the job execution,
    to delete the working directory
    created by :func:`~aeneas.executejob.ExecuteJob.load_job_from_container`
    when creating the job object.

    :param job: the job to be executed
    :type  job: :class:`~aeneas.job.Job`
    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :raises: :class:`~aeneas.executejob.ExecuteJobInputError`: if ``job`` is not an instance of ``Job``
    """

    def __init__(self, job=None, rconf=None):
        super().__init__(rconf=rconf)
        self.job = job
        self.working_directory = None
        self.tmp_directory = None
        if job is not None:
            self.load_job(self.job)

    def load_job(self, job):
        """
        Load the job from the given ``Job`` object.

        :param job: the job to load
        :type  job: :class:`~aeneas.job.Job`
        :raises: :class:`~aeneas.executejob.ExecuteJobInputError`: if ``job`` is not an instance of :class:`~aeneas.job.Job`
        """
        if not isinstance(job, Job):
            raise ExecuteJobInputError("`job` is not an instance of Job")
        self.job = job

    def load_job_from_container(self, container_path, config_string=None):
        """
        Load the job from the given :class:`aeneas.container.Container` object.

        If ``config_string`` is ``None``,
        the container must contain a configuration file;
        otherwise use the provided config string
        (i.e., the wizard case).

        :param string container_path: the path to the input container
        :param string config_string: the configuration string (from wizard)
        :raises: :class:`~aeneas.executejob.ExecuteJobInputError`: if the given container does not contain a valid :class:`~aeneas.job.Job`
        """
        logger.debug("Loading job from container...")

        # FIXME: After switching to `tempfile`, it seems that `self.clean()` is
        # not called always and the temporary directories are not explicitly clean up.

        # create working directory where the input container
        # will be decompressed
        self.working_directory = tempfile.TemporaryDirectory(
            dir=self.rconf[RuntimeConfiguration.TMP_PATH]
        )
        logger.debug("Created working directory %r", self.working_directory.name)

        try:
            logger.debug("Decompressing input container...")
            input_container = Container(container_path)
            input_container.decompress(self.working_directory.name)
            logger.debug("Decompressing input container... done")
        except Exception as exc:
            self.clean()
            raise ExecuteJobInputError(
                f"Unable to decompress container {container_path!r}: {exc}"
            ) from exc

        try:
            logger.debug("Creating job from working directory...")
            working_container = Container(self.working_directory.name)
            analyzer = AnalyzeContainer(working_container)
            self.job = analyzer.analyze(config_string=config_string)
            logger.debug("Creating job from working directory... done")
        except Exception as exc:
            self.clean()
            raise ExecuteJobInputError(
                f"Unable to analyze container {container_path!r}: {exc}"
            ) from exc

        if self.job is None:
            raise ExecuteJobInputError(
                f"The container {container_path!r} does not contain a valid Job"
            )

        try:
            # set absolute path for text file and audio file
            # for each task in the job
            logger.debug("Setting absolute paths for tasks...")
            for task in self.job.tasks:
                task.text_file_path_absolute = gf.norm_join(
                    self.working_directory.name, task.text_file_path
                )
                task.audio_file_path_absolute = gf.norm_join(
                    self.working_directory.name, task.audio_file_path
                )
            logger.debug("Setting absolute paths for tasks... done")

            logger.debug("Loading job from container: succeeded")
        except Exception as exc:
            self.clean()
            raise ExecuteJobInputError(
                "Error while setting absolute paths for tasks"
            ) from exc

    def execute(self):
        """
        Execute the job, that is, execute all of its tasks.

        Each produced sync map will be stored
        inside the corresponding task object.

        :raises: :class:`~aeneas.executejob.ExecuteJobExecutionError`: if there is a problem during the job execution
        """
        logger.debug("Executing job")

        if self.job is None:
            raise ExecuteJobExecutionError("The job object is None")
        if len(self.job) == 0:
            raise ExecuteJobExecutionError("The job has no tasks")
        job_max_tasks = self.rconf[RuntimeConfiguration.JOB_MAX_TASKS]
        if job_max_tasks > 0 and len(self.job) > job_max_tasks:
            raise ExecuteJobExecutionError(
                f"The Job has {len(self.job)} Tasks, "
                f"more than the maximum allowed ({job_max_tasks})."
            )
        logger.debug("Number of tasks: %d", len(self.job))

        for task in self.job.tasks:
            try:
                custom_id = task.configuration["custom_id"]
                logger.debug("Executing task %r...", custom_id)
                executor = ExecuteTask(task, rconf=self.rconf)
                executor.execute()
                logger.debug("Executing task %r... done", custom_id)
            except Exception as exc:
                raise ExecuteJobExecutionError(
                    f"Error while executing task {custom_id!r}"
                ) from exc
            logger.debug("Executing task: succeeded")

        logger.debug("Executing job: succeeded")

    def write_output_container(self, output_directory_path):
        """
        Write the output container for this job.

        Return the path to output container,
        which is the concatenation of ``output_directory_path``
        and of the output container file or directory name.

        :param string output_directory_path: the path to a directory where
                                             the output container must be created
        :rtype: string
        :raises: :class:`~aeneas.executejob.ExecuteJobOutputError`: if there is a problem while writing the output container
        """
        logger.debug("Writing output container for this job")

        if self.job is None:
            raise ExecuteJobOutputError("The job object is None")
        if len(self.job) == 0:
            raise ExecuteJobOutputError("The job has no tasks")
        logger.debug("Number of tasks: %d", len(self.job))

        # create temporary directory where the sync map files
        # will be created
        # this temporary directory will be compressed into
        # the output container
        self.tmp_directory = tempfile.TemporaryDirectory(
            dir=self.rconf[RuntimeConfiguration.TMP_PATH]
        )
        logger.debug("Created temporary directory %r", self.tmp_directory.name)

        for task in self.job.tasks:
            custom_id = task.configuration["custom_id"]

            # check if the task has sync map and sync map file path
            if task.sync_map_file_path is None:
                raise ExecuteJobOutputError(
                    f"Task {custom_id!r} has sync_map_file_path not set"
                )
            if task.sync_map is None:
                raise ExecuteJobOutputError(f"Task {custom_id!r} has sync_map not set")

            try:
                # output sync map
                logger.debug("Outputting sync map for task %r...", custom_id)
                task.output_sync_map_file(self.tmp_directory.name)
                logger.debug("Outputting sync map for task %r... done", custom_id)
            except Exception as exc:
                raise ExecuteJobOutputError(
                    f"Error while outputting sync map for task {custom_id!r}"
                ) from exc

        # get output container info
        output_container_format = self.job.configuration["o_container_format"]
        logger.debug("Output container format: %r", output_container_format)
        output_file_name = self.job.configuration["o_name"]
        if output_container_format != ContainerFormat.UNPACKED and (
            not output_file_name.endswith(output_container_format)
        ):
            logger.debug("Adding extension to output_file_name")
            output_file_name += "." + output_container_format
        logger.debug("Output file name: %r", output_file_name)
        output_file_path = gf.norm_join(output_directory_path, output_file_name)
        logger.debug("Output file path: %r", output_file_path)

        try:
            logger.debug("Compressing...")
            container = Container(output_file_path, output_container_format)
            container.compress(self.tmp_directory.name)
            logger.debug("Compressing... done")
            logger.debug("Created output file: %r", output_file_path)
            logger.debug("Writing output container for this job: succeeded")
            return output_file_path
        except Exception as exc:
            raise ExecuteJobOutputError("Error while compressing") from exc
        finally:
            self.clean(False)

        return None

    def clean(self, remove_working_directory: bool = True):
        """
        Remove the temporary directory.
        If ``remove_working_directory`` is ``True``
        remove the working directory as well,
        otherwise just remove the temporary directory.

        :param bool remove_working_directory: if ``True``, remove
                                              the working directory as well
        """
        if remove_working_directory and self.working_directory is not None:
            logger.debug("Removing working directory... ")
            self.working_directory.cleanup()
            logger.debug("Removing working directory... done")

        if self.tmp_directory is not None:
            logger.debug("Removing temporary directory... ")
            self.tmp_directory.cleanup()
            self.tmp_directory = None
            logger.debug("Removing temporary directory... done")
