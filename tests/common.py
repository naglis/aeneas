import unittest
import typing
import os
import tempfile

from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.tools.execute_task import ExecuteTaskCLI


slow_test = unittest.skipIf(
    (val := os.getenv("UNITTEST_RUN_SLOW_TESTS")) is None or val.strip() == "0",
    "slow tests are disabled. Set `UNITTEST_RUN_SLOW_TESTS=1` in the environment to enable them.",
)

EXTRA_TEST_PATH = os.path.join(os.path.expanduser("~"), ".aeneas.conf")
extra_test = unittest.skipIf(
    not os.path.isfile(EXTRA_TEST_PATH),
    f"extra tests are disabled (path {EXTRA_TEST_PATH!r} does not exist).",
)

BENCH_DIR = os.path.join(os.path.expanduser("~"), ".aeneas", "benchmark_input")
bench_test = unittest.skipIf(
    not os.path.isdir(BENCH_DIR),
    f"bench tests are disabled (directory {BENCH_DIR!r} does not exist).",
)


class BaseCase(unittest.TestCase):
    # Do not truncate diffs.
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmp_dir = tempfile.TemporaryDirectory(prefix="aeneas.test.")
        cls.addClassCleanup(cls.tmp_dir.cleanup)

        cls.rconf = RuntimeConfiguration()
        cls.rconf[RuntimeConfiguration.TMP_PATH] = cls.tmp_dir.name

    @classmethod
    def file_path(cls, path: str) -> str:
        return os.path.join(os.path.dirname(__file__), *path.split("/"))


class ExecuteCLICase(BaseCase):
    CLI_CLS: typing.ClassVar

    def execute(
        self, parameters: typing.Sequence[tuple[str, str]], expected_exit_code: int
    ):
        arguments = ["placeholder"]
        with tempfile.TemporaryDirectory(
            prefix="cli.", dir=self.tmp_dir.name
        ) as temp_dir:
            for p_type, p_value in parameters:
                if p_type == "in":
                    arguments.append(self.file_path(p_value))
                elif p_type == "out":
                    arguments.append(os.path.join(temp_dir, p_value))
                else:
                    arguments.append(p_value)

            exit_code = self.CLI_CLS(use_sys=False, rconf=self.rconf).run(
                arguments=arguments
            )

        self.assertEqual(exit_code, expected_exit_code)


class ExecuteTaskCLICase(ExecuteCLICase):
    CLI_CLS = ExecuteTaskCLI
