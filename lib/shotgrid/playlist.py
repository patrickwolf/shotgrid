#!/usr/bin/env python

__doc__ = """
Contains Playlist base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log
from shotgrid.version import Version


class Playlist(Entity):
    """Shotgrid Playlist entity."""

    entity_type = "Playlist"

    fields = [
        "id",
        "code",
        "description",
        "locked",
        "versions",
    ]

    def __init__(self, *args, **kwargs):
        super(Playlist, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)

    def add_versions(self, versions):
        """Adds a list of Versions to this playlist.

        :param versions: list of Versions
        """
        return self.update(
            versions=[v.data for v in versions], update_mode={"versions": "add"}
        )

    def get_versions(self, code=None, filters=None, fields=None):
        """Gets a list of versions for this playlist.

        :param code: sg version code
        :param filters: additional filters (optional)
        :param fields: which fields to return (optional)
        :return: list of versions for this playlist
        :raise: gaierror if can't connect to shotgrid.
        """
        versions = []

        fields = fields or Version.fields
        params = [["playlists", "is", self.data]]

        if code:
            params.append(["code", "is", code])

        if filters:
            params.extend(filters)

        results = self.api().find("Version", params, fields)

        for r in results:
            versions.append(Version(self, r))

        return versions

    def remove_versions(self, versions):
        """Removes a list of Versions from this playlist.

        :param versions: list of Versions
        """
        return self.update(
            versions=[v.data for v in versions], update_mode={"versions": "remove"}
        )
