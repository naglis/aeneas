import unittest
import typing
import os
import tempfile

from aeneas.tools.execute_task import ExecuteTaskCLI
from aeneas.tools.execute_job import ExecuteJobCLI

import aeneas.globalfunctions as gf


slow_test = unittest.skipIf(
    (val := os.getenv("UNITTEST_RUN_SLOW_TESTS")) is None or val.strip() == "0",
    "slow tests are disabled. Set `UNITTEST_RUN_SLOW_TESTS=1` in the environment to enable them.",
)


class ExecuteCLICase(unittest.TestCase):
    CLI_CLS: typing.ClassVar

    def execute(
        self, parameters: typing.Sequence[tuple[str, str]], expected_exit_code: int
    ):
        params = ["placeholder"]
        with tempfile.TemporaryDirectory(prefix="aeneas.") as temp_dir:
            for p_type, p_value in parameters:
                if p_type == "in":
                    params.append(gf.absolute_path(p_value, __file__))
                elif p_type == "out":
                    params.append(os.path.join(temp_dir, p_value))
                else:
                    params.append(p_value)

            exit_code = self.CLI_CLS(use_sys=False).run(arguments=params)

        self.assertEqual(exit_code, expected_exit_code)


class ExecuteJobCLICase(ExecuteCLICase):
    CLI_CLS = ExecuteJobCLI


class ExecuteTaskCLICase(ExecuteCLICase):
    CLI_CLS = ExecuteTaskCLI
