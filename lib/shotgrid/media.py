#!/usr/bin/env python

__doc__ = """
Contains Movie base classes.
"""

import os

import requests

from shotgrid.base import Entity
from shotgrid.logger import log


def stream_download(filename, url, chunk=4096):
    """downloads/streams a file in chunks."""

    from contextlib import closing

    with closing(requests.get(url, stream=True)) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk):
                if chunk:
                    f.write(chunk)
        r.close()

    return filename


class Movie(Entity):
    """Wrapper class for the sg_uploaded_movie entity."""

    def __init__(self, *args, **kwargs):
        super(Movie, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.name)

    def download(self, folder=None):
        """Downloads this movie to a specified folder on disk.

        :param folder: which folder to write the movie to
        :return: download file path
        """
        name = self.data.name
        if folder:
            name = os.path.sep.join([folder, name])
        dl = stream_download(name, self.data.url)
        if not os.path.exists(dl):
            log.error("download failed")
        return dl
