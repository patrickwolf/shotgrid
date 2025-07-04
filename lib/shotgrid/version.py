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
Contains Version base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class Version(Entity):
    """Shotgrid Version entity."""

    entity_type = "Version"

    fields = [
        "id",
        "description",
        "code",
        "tags",
        "entity",
        "published_files",
        "sg_path_to_frames",
        "sg_version_type",
        "sg_status_list",
        "sg_uploaded_movie",
        "sg_ingests"
    ]

    def __init__(self, *args, **kwargs):
        super(Version, self).__init__(*args, **kwargs)

    @property
    def movie(self):
        from shotgrid.media import Movie

        return Movie(self, self.data.sg_uploaded_movie)

    def create_published_file(self, code: str, task: dict, **data):
        """Creates a new Version with this shot as the parent.

        :param code: version name
        :param data: version data dictionary
        :return: new Version object
        """
        from shotgrid.publishedfile import PublishedFile

        data.update({"code": code, "entity": self.parent().data, "version": self.data, "task": task})
        results = self.create(PublishedFile.entity_type, data=data)
        return PublishedFile(self, results)

    def get_published_files(self, code: str = None, id: int = None, filters: list = None, fields: list = None):
        params = [["version", "is", self.data]]

        if filters is not None:
            params.extend(filters)

        return self._get_published_files(code=code, id=id, filters=params, fields=fields)
