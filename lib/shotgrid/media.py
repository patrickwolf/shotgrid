#!/usr/bin/env python
#
# Copyright (c) 2024, Ryan Galloway (ryan@rsgalloway.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

__doc__ = """
Contains Movie base classes.
"""

import os

import requests
import shotgun_api3
from shotgrid.base import Entity
from shotgrid.logger import log


def stream_download(filename: str, url: str, chunk: int = 4096):
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

    def download(self, folder: str = None):
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

    def upload(self, file_path: str = None) -> bool:
        """Upload a file to the entity's sg_uploaded_movie field."""
        if not file_path or not os.path.exists(file_path):
            log.error(f"File not found: {file_path}")
            return False

        attachment_exists = self.check_attachment_exists('sg_uploaded_movie')
        if attachment_exists:
            log.info(f"Attachment already exists for {self.parent().entity_type} {self.parent().id()}")
            return False

        for i in range(10):
            try:
                # Let the API handle the file opening and closing
                result = self.api().upload(
                    self.parent().entity_type,
                    self.parent().id(),
                    file_path,
                    field_name='sg_uploaded_movie'
                )
                if result:
                    log.info(f'Uploaded {file_path} to {self.parent().entity_type} {self.parent().id()}')
                    return True
            except shotgun_api3.ShotgunError as e:
                log.error(f"Upload failed on attempt {i + 1}: {e}")
                if i < 9:
                    log.info("Retrying upload...")

        return False

    # def upload2(self, entity_type: str, entity_id: int, field_name: str, file_path: str = None) -> bool:
    #     attachment_exists = self.check_attachment_exists(entity['type'], entity['id'])
    #     if not attachment_exists:
    #         if self.api().upload(entity_type, entity_id, file_path, field_name):
    #             log.info('Uploaded %s to %s %s' % (file_path, entity_type, entity_id))
    #             return True
    #     return False

    def check_attachment_exists(self, field_name: str = 'sg_uploaded_movie'):
        """For file mode only, if uploading files to a specific field, checks to see
        if there is already a file in that entity field. File upload will fail if
        a file already exists on the entity so we don't accidentally blow things
        away. You can disable this if you like.
        """
        # not applicable if we're not uploading to a field
        if not field_name:
            return False
        result = self.api().find_one(self.parent().entity_type, [['id', 'is', self.parent().id()]], [field_name])
        if result[field_name]:
            log.debug('File already exists for %s %s in field %s' %
                      (self.parent().entity_type, self.parent().id(), field_name))
            return True
        return False
