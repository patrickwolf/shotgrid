#!/usr/bin/env python

__doc__ = """
Contains Sequence base class.
"""

import socket

from shotgrid.base import Entity
from shotgrid.logger import log
from shotgrid.shot import Shot


class Sequence(Entity):
    """Shotgrid Sequence entity."""

    entity_type = "Sequence"

    fields = [
        "id",
        "description",
        "assets",
        "code",
        "shots",
        "sg_sequence_type",
        "sg_status_list",
    ]

    def __init__(self, *args, **kwargs):
        super(Sequence, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)

    def create_shot(self, code, **data):
        """Creates a new Shot under this Sequence.

        :param code: shot code
        :return: new Shot objects
        """

        data.update(
            {"project": self.get_project().data, "sg_sequence": self.data, "code": code}
        )
        results = self.create("Shot", data=data)
        return Shot(self, results)

    def get_shots(self, code=None, fields=None):
        """Gets a list of shots from shotgrid for this project.

        :param code: shot code
        :param fields: which fields to return (optional)
        :return: shot list from shotgrid for given project
        :raise: socket.gaierror if can't connect to shotgrid.
        """

        fields = fields or Shot.fields
        params = [["sg_sequence", "is", self.data]]

        if code is not None:
            params.append(["code", "is", code])

        try:
            results = self.api().find("Shot", params, fields=fields)
            shots = list()
            for r in results:
                shots.append(Shot(self, data=r))
            return shots

        except socket.gaierror as e:
            raise
