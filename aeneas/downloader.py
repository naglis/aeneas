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

* :class:`~aeneas.downloader.DownloadError`, which represents an error occurred
  while downloading a Web resource.
* :class:`~aeneas.downloader.Downloader`, which download files from various Web sources.

.. note:: This module requires Python module ``youtube-dl`` (``pip install youtube-dl``).
"""

import logging
import time
import tempfile

from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """
    Error raised when a given URL is not valid or
    it cannot be downloaded because of temporary
    network issues.
    """


class Downloader(Configurable):
    """
    Download files from various Web sources.
    At the moment, only YouTube videos
    are officially supported.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    def audio_from_youtube(
        self,
        source_url: str,
        download: bool = True,
        output_file_path: str | None = None,
        download_format: int | None = None,
        largest_audio: bool = True,
    ):
        """
        Download an audio stream from a YouTube video,
        and save it to file.

        If ``download`` is ``False``, return the list
        of available audiostreams but do not download.

        Otherwise, download the audio stream best matching
        the provided parameters, as follows.
        If ``download_format`` is not ``None``,
        download the audio stream with the specified format.
        If ``largest_audio`` is ``True``,
        download the largest audiostream;
        otherwise, download the smallest audiostream.
        If ``preferred_format`` is not ``None``,
        download the audiostream having that format.
        The latter option works in combination with ``largest_audio``.

        Return the path of the downloaded file.

        :param string source_url: the URL of the YouTube video
        :param bool download: if ``True``, download the audio stream
                              best matching ``preferred_index`` or
                              ``preferred_format`` and ``largest_audio``;
                              if ``False``, return the list of available audio streams
        :param string output_file_path: the path where the downloaded audio should be saved;
                                        if ``None``, create a temporary file
        :param int download_format: download the audio stream with the given format
        :param bool largest_audio: if ``True``, download the largest audio stream available;
                                   if ``False``, download the smallest one.
        :rtype: string or list of dict
        :raises: ImportError: if ``youtube-dl`` is not installed
        :raises: OSError: if ``output_file_path`` cannot be written
        :raises: :class:`~aeneas.downloader.DownloadError`: if ``source_url`` is not a valid YouTube URL
                                                            or it cannot be downloaded e.g. for temporary
                                                            network issues
        """

        def _list_audiostreams(self, source_url: str):
            """
            Return a list of dicts, each describing
            an available audiostream for the given ``source_url``.
            """
            logger.debug("Getting audiostreams...")
            audiostreams = []
            options = {
                "download": False,
                "quiet": True,
                "skip_download": True,
            }
            with youtube_dl.YoutubeDL(options) as ydl:
                info = ydl.extract_info(source_url, download=False)
                audio_formats = [
                    f
                    for f in info["formats"]
                    if f["vcodec"] == "none" and f["acodec"] != "none"
                ]
                for a in audio_formats:
                    audiostreams.append(
                        {
                            "format": a["format"].split(" ")[0],
                            "filesize": a["filesize"],
                            "ext": a["ext"],
                            "abr": a["abr"],
                        }
                    )
            logger.debug("Getting audiostreams... done")
            return audiostreams

        def _select_audiostream(
            self, audiostreams, download_format=None, largest_audio=False
        ):
            """
            Select the best-matching audiostream:
            if a ``download_format`` is given, use it,
            otherwise act according to ``largest_audio``.
            If ``download_format`` is not matching any
            of the available audiostreams, then just act
            according to ``largest_audio``.
            """
            logger.debug("Selecting best-matching audiostream...")
            selected = None
            if download_format is not None:
                matching = [a for a in audiostreams if a["format"] == download_format]
                if len(matching) > 0:
                    selected = matching[0]
            if selected is None:
                sa = sorted(audiostreams, key=lambda x: x["filesize"])
                selected = sa[-1] if largest_audio else sa[0]
            logger.debug("Selecting best-matching audiostream... done")
            return selected

        def _compose_output_file_path(self, extension, output_file_path=None):
            """
            If ``output_file_path`` is given, use it.
            Otherwise (``output_file_path`` is ``None``),
            create a temporary file with the correct extension.
            """
            logger.debug("Determining output file path...")
            if output_file_path is None:
                logger.debug("output_file_path is None: creating temp file")
                with tempfile.NamedTemporaryFile(
                    suffix=f".{extension}",
                    dir=self.rconf[RuntimeConfiguration.TMP_PATH],
                ) as tmp_file:
                    output_file_path = tmp_file.name
            else:
                logger.debug(
                    "output_file_path is not None: cheking that file can be written"
                )
                if not gf.file_can_be_written(output_file_path):
                    raise OSError(
                        f"Path {output_file_path!r} cannot be written. Wrong permissions?"
                    )
            logger.debug("Determining output file path... done")
            logger.debug("Output file path is %r", output_file_path)
            return output_file_path

        def _download_audiostream(self, source_url, fmt, output_path):
            logger.debug("Downloading audiostream...")
            options = {
                "download": True,
                "format": fmt,
                "outtmpl": output_path,
                "quiet": True,
                "skip_download": False,
            }
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([source_url])
            logger.debug("Downloading audiostream... done")

        try:
            import youtube_dl
        except ImportError as exc:
            raise ImportError("Python module youtube-dl is not installed") from exc

        # retry parameters
        sleep_delay = self.rconf[RuntimeConfiguration.DOWNLOADER_SLEEP]
        attempts = self.rconf[RuntimeConfiguration.DOWNLOADER_RETRY_ATTEMPTS]
        logger.debug("Sleep delay:    %.3f", sleep_delay)
        logger.debug("Retry attempts: %d", attempts)

        # get audiostreams
        att = attempts
        while att > 0:
            logger.debug("Sleeping to throttle API usage...")
            time.sleep(sleep_delay)
            logger.debug("Sleeping to throttle API usage... done")
            try:
                audiostreams = _list_audiostreams(self, source_url)
                break
            except Exception:
                logger.warning("Unable to list audio streams, retry")
                att -= 1
        if att <= 0:
            raise DownloadError(
                "All downloader requests failed: wrong URL or you are offline?"
            )

        if not download:
            logger.debug("Returning list of audiostreams")
            return audiostreams

        # download the best-matching audiostream
        if len(audiostreams) == 0:
            raise OSError("No audiostreams available for the provided URL")
        audiostream = _select_audiostream(
            self, audiostreams, download_format, largest_audio
        )
        output_path = _compose_output_file_path(
            self, audiostream["ext"], output_file_path
        )
        att = attempts
        while att > 0:
            logger.debug("Sleeping to throttle API usage...")
            time.sleep(sleep_delay)
            logger.debug("Sleeping to throttle API usage... done")
            try:
                _download_audiostream(
                    self, source_url, audiostream["format"], output_path
                )
                break
            except Exception:
                logger.warning("Unable to download audio streams, retry", exc_info=True)
                att -= 1
        if att <= 0:
            raise DownloadError(
                "All downloader requests failed: wrong URL or you are offline?"
            )

        return output_path
