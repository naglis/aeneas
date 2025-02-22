import argparse
import logging
import decimal
import os.path
import typing
import tempfile
import sys

from aeneas import globalconstants as gc, globalfunctions as gf
from aeneas.adjustboundaryalgorithm import AdjustBoundaryAlgorithm
from aeneas.exacttiming import TimeValue
from aeneas.executetask import ExecuteTask
from aeneas.idsortingalgorithm import IDSortingAlgorithm
from aeneas.language import Language
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.syncmap.format import SyncMapFormat
from aeneas.syncmap.fragment import FragmentType
from aeneas.syncmap.headtailformat import SyncMapHeadTailFormat
from aeneas.task import Task, TaskConfiguration
from aeneas.textfile import TextFileFormat


logger = logging.getLogger(__name__)


def parse_time_value(v: str) -> TimeValue:
    if ":" in v:
        return gf.time_from_hhmmssmmm(v)
    return gf.time_from_ssmmm(v)


def parse_adjust_percent(v: str) -> int:
    percent = int(v)
    if not 0 <= percent <= 100:
        raise ValueError("value must be from interval [0, 100]")

    return percent


def parse_adjust_rate(v: str) -> decimal.Decimal:
    rate = decimal.Decimal(v)
    if rate.is_nan() or rate.is_infinite() or rate <= 0:
        raise ValueError("value must be positive")

    return rate


def get_task_config_from_args(args: argparse.Namespace) -> TaskConfiguration:
    task_config = TaskConfiguration()
    task_config[gc.PPN_TASK_LANGUAGE] = args.language

    task_config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.UNPARSED_IMG
    task_config[gc.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX] = args.id_regex
    task_config[gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT] = args.id_sort
    if args.ignore_text_regex:
        task_config[gc.PPN_TASK_IS_TEXT_FILE_IGNORE_REGEX] = args.ignore_text_regex

    task_config[gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF] = args.audio_ref
    task_config[gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF] = args.page_ref
    task_config[gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT] = SyncMapHeadTailFormat.HIDDEN
    task_config[gc.PPN_TASK_OS_FILE_FORMAT] = SyncMapFormat.SMIL

    task_config[gc.PPN_TASK_ADJUST_BOUNDARY_NO_ZERO] = args.no_zero
    if args.min_nonspeech is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_MIN] = args.min_nonspeech
    if args.nonspeech_string:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_STRING] = (
            args.nonspeech_string
        )

    if args.adjust_aftercurrent is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.AFTERCURRENT
        )
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_AFTERCURRENT_VALUE] = (
            args.adjust_aftercurrent
        )
    elif args.adjust_beforenext is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.BEFORENEXT
        )
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_BEFORENEXT_VALUE] = (
            args.adjust_beforenext
        )
    elif args.adjust_offset is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.OFFSET
        )
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_OFFSET_VALUE] = args.adjust_offset
    elif args.adjust_percent is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.PERCENT
        )
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_PERCENT_VALUE] = args.adjust_percent
    elif args.adjust_rate is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.RATE
        )
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE] = args.adjust_rate
    elif args.adjust_rateaggresive is not None:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.RATEAGGRESSIVE
        )
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE] = args.adjust_rateaggressive
    else:
        task_config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = (
            AdjustBoundaryAlgorithm.AUTO
        )

    if args.audio_start is not None:
        task_config[gc.PPN_TASK_IS_AUDIO_FILE_HEAD_LENGTH] = args.audio_start
    if args.audio_length is not None:
        task_config[gc.PPN_TASK_IS_AUDIO_FILE_PROCESS_LENGTH] = args.audio_length
    if args.audio_end is not None:
        task_config[gc.PPN_TASK_IS_AUDIO_FILE_TAIL_LENGTH] = args.audio_end

    return task_config


def do_sync(args: argparse.Namespace, rconf: RuntimeConfiguration) -> int:
    audio_path = args.audio_path
    text_path = args.text_path
    output_path = args.output_path
    html_file_path = None

    if args.presets_word:
        rconf[RuntimeConfiguration.MFCC_MASK_NONSPEECH] = True
        rconf[RuntimeConfiguration.MFCC_MASK_NONSPEECH_L3] = True

    # TODO: Check for the availability of C extensions.

    task = Task(config=get_task_config_from_args(args))
    task.audio_file_path_absolute = audio_path
    task.text_file_path_absolute = text_path
    task.sync_map_file_path_absolute = output_path

    ExecuteTask(task=task, rconf=rconf).execute()

    path = task.output_sync_map_file()
    print(f"Wrote SMIL to {path!r}", file=sys.stderr)

    if args.output_html:
        html_file_path = output_path + ".html"
        parameters = {
            gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT: SyncMapHeadTailFormat.HIDDEN,
            gc.PPN_TASK_OS_FILE_FORMAT: SyncMapFormat.SMIL,
            gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF: args.audio_ref,
            gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF: args.page_ref,
        }
        # Remove the `.html` and the output format suffix (if any).
        basename = os.path.splitext(
            os.path.splitext(os.path.basename(html_file_path))[0]
        )[0]

        logger.info("Creating output HTML file...")
        with open(html_file_path, mode="w", encoding="utf-8") as f:
            task.sync_map.dump_finetuneas_html(
                f,
                basename,
                audio_path,
                parameters=parameters,
            )
        logger.info(f"Created file {html_file_path!r}")

    if args.print_zero_duration:
        zero_duration = (
            leaf
            for leaf in task.sync_map_leaves(FragmentType.REGULAR)
            if leaf.begin == leaf.end
        )
        if (fragment := next(zero_duration, None)) is not None:
            print("Fragments with zero duration:")
            print(fragment.pretty_print)
            for fragment in zero_duration:
                print(fragment.pretty_print)

    if args.print_rate:
        print("Fragments with rates:")
        for fragment in task.sync_map_leaves(FragmentType.REGULAR):
            print(f"  {fragment.pretty_print}\t{fragment.rate or 0.0:.3f}")

    if args.print_faster_rate:
        max_rate = task.configuration["aba_rate_value"]
        if max_rate is not None:
            delta = decimal.Decimal("0.001")
            faster = (
                leaf
                for leaf in task.sync_map_leaves(FragmentType.REGULAR)
                if leaf.rate >= max_rate + delta
            )
            if (fragment := next(faster, None)) is not None:
                print(f"Fragments with rate greater than {max_rate:.3f}:")
                print(f"  {fragment.pretty_print}\t{fragment.rate or 0.0:.3f}")
                for fragment in faster:
                    print(f"  {fragment.pretty_print}\t{fragment.rate or 0.0:.3f}")

    return 0


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbose output. Can be repeated",
    )
    parser.add_argument(
        "-l",
        "--log",
        metavar="FILE",
        help="output log messages to specified %(metavar)s",
    )
    parser.add_argument(
        "-r",
        "--runtime-configuration",
        metavar="CONF",
        help="apply runtime configuration %(metavar)s",
    )

    subparsers = parser.add_subparsers()

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("audio_path", help="path to the audio input file")
    sync_parser.add_argument("text_path", help="path to the HTML input file")
    sync_parser.add_argument("output_path", help="path to the SMIL output file")
    sync_parser.add_argument(
        "--id-regex",
        metavar="REGEX",
        required=True,
        help='regex to match "id" attributes for text fragments',
    )
    sync_parser.add_argument(
        "--id-sort",
        metavar="ALGO",
        help="algorithm to sort matched text fragments by ID. Default: %(default)s",
        default=IDSortingAlgorithm.UNSORTED,
        choices=IDSortingAlgorithm.ALLOWED_VALUES,
    )
    sync_parser.add_argument(
        "--audio-ref",
        required=True,
        help='the value of the "src" attribute for the <audio> element in the SMIL file',
    )
    sync_parser.add_argument(
        "--page-ref",
        required=True,
        help='the value of the "src" attribute for the <text> element in the SMIL file',
    )
    sync_parser.add_argument(
        "--language",
        metavar="CODE",
        required=True,
        # TODO: Fix using `Language` enum
        choices=[v.value for v in (Language.ENG, Language.LIT)],
    )
    sync_parser.add_argument(
        "--audio-start",
        metavar="HH:MM:SS",
        type=parse_time_value,
        help="if specified, alignment will start at this position in the audio file",
    )
    sync_parser.add_argument(
        "--audio-length",
        metavar="HH:MM:SS",
        type=parse_time_value,
        help="if specified, alignment will process only this duration of audio in the audio file",
    )
    sync_parser.add_argument(
        "--audio-end",
        metavar="HH:MM:SS",
        type=parse_time_value,
        help="if specified, alignment will end at this position in the audio file",
    )
    adjust_group = sync_parser.add_argument_group(title="boundary adjustion options")
    adjust_group.add_argument(
        "--no-zero",
        help="if specified, do not allow zero-length fragments",
        action="store_true",
    )
    adjust_group.add_argument(
        "--min-nonspeech",
        metavar="HH:MM:SS",
        help="minimum long nonspeech duration",
        type=parse_time_value,
    )
    adjust_group.add_argument(
        "--nonspeech-string",
        metavar="STRING",
        help="replace long nonspeech with this string or specify REMOVE",
    )
    adjust_mutex_group = adjust_group.add_mutually_exclusive_group()
    adjust_mutex_group.add_argument(
        "--adjust-aftercurrent",
        type=parse_time_value,
        metavar="HH:MM:SS",
        help=(
            "set the boundary at %(metavar)s seconds after the end of the current fragment, "
            "if the current boundary falls inside a nonspeech interval. If not, no adjustment is made."
        ),
    )
    adjust_mutex_group.add_argument(
        "--adjust-beforenext",
        type=parse_time_value,
        metavar="HH:MM:SS",
        help=(
            "set the boundary at %(metavar)s seconds before the beginning of the next fragment, "
            "if the current boundary falls inside a nonspeech interval. If not, no adjustment is made."
        ),
    )
    adjust_mutex_group.add_argument(
        "--adjust-offset",
        type=parse_time_value,
        metavar="HH:MM:SS",
        help="offset the current boundaries by %(metavar)s seconds. The %(metavar)s can be negative or positive.",
    )
    adjust_mutex_group.add_argument(
        "--adjust-percent",
        type=parse_adjust_percent,
        metavar="VALUE",
        help=(
            "set the boundary at %(metavar)s percent of the nonspeech interval between "
            "the current and the next fragment, if the current boundary falls inside "
            "a nonspeech interval. If not, no adjustment is made. The %(metavar)s must be an integer between [0, 100]."
        ),
    )
    adjust_mutex_group.add_argument(
        "--adjust-rate",
        type=parse_adjust_rate,
        metavar="VALUE",
        help=(
            "Adjust boundaries trying to respect the %(metavar)s characters/second constraint. "
            "The %(metavar)s must be positive. "
            "First, the rates of all fragments are computed, using the current boundaries. "
            "For those fragments exceeding %(metavar)s characters/second, "
            "the algorithm will try to move the end boundary forward, "
            "so that its time interval increases (and hence its rate decreases). "
            "Clearly, it is possible that not all fragments can be adjusted this way: "
            "for example, if you have three consecutive fragments exceeding %(metavar)s, "
            "the middle one cannot be stretched."
        ),
    )
    adjust_mutex_group.add_argument(
        "--adjust-rateaggresive",
        type=parse_adjust_rate,
        metavar="VALUE",
        help=(
            "Adjust boundaries trying to respect the %(metavar)s characters/second constraint, in aggressive mode. "
            "The %(metavar)s must be positive. "
            "First, the rates of all fragments are computed, using the current boundaries. "
            "For those fragments exceeding %(metavar)s characters/second, "
            "the algorithm will try to move the end boundary forward, "
            "so that its time interval increases (and hence its rate decreases). "
            "If moving the end boundary is not possible, "
            "or it is not enough to keep the rate below %(metavar)s, "
            "the algorithm will try to move the begin boundary back; "
            "this is the difference with the less aggressive `rate` algorithm. "
            "Clearly, it is possible that not all fragments can be adjusted this way: "
            "for example, if you have three consecutive fragments exceeding %(metavar)s, "
            "the middle one cannot be stretched."
        ),
    )

    sync_parser.add_argument(
        "--ignore-text-regex",
        metavar="REGEX",
        help="for the alignment, ignore text matched by %(metavar)s",
    )
    sync_parser.add_argument(
        "--output-html", action="store_true", help="output finetuneas HTML"
    )
    sync_parser.add_argument(
        "--presets-word",
        action="store_true",
        help="apply presets for word-level alignment (MFCC masking)",
    )
    sync_parser.add_argument(
        "--print-faster-rate",
        action="store_true",
        help="print fragments with rate > task_adjust_boundary_rate_value",
    )
    sync_parser.add_argument(
        "--print-rate", action="store_true", help="print rate of each fragment"
    )
    sync_parser.add_argument(
        "--print-zero-duration",
        action="store_true",
        help="print fragments with zero duration",
    )
    sync_parser.set_defaults(func=do_sync)

    args = parser.parse_args(argv)

    loglevel = logging.WARNING
    logformat = "%(levelname)s %(name)s %(message)s"
    if args.verbose == 1:
        loglevel = logging.INFO
    elif args.verbose > 1:
        loglevel = logging.DEBUG
        logformat = "%(asctime)s %(levelname)s %(name)s %(message)s"

    logging.basicConfig(filename=args.log, level=loglevel, format=logformat)

    if hasattr(args, "func"):
        rconf = RuntimeConfiguration(args.runtime_configuration)
        with tempfile.TemporaryDirectory(
            prefix="aeneas.", dir=rconf[RuntimeConfiguration.TMP_PATH]
        ) as temp_dir:
            rconf[RuntimeConfiguration.TMP_PATH] = temp_dir
            return args.func(args, rconf)
    else:
        parser.print_usage()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
