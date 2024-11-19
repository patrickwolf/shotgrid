#!/usr/bin/env python

__doc__ = """
Contains Shot base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class Shot(Entity):
    """Shotgrid Shot entity."""

    entity_type = "Shot"

    fields = [
        "id",
        "code",
        "description",
        "assets",
        "sg_sequence",
        "sg_status_list",
        "versions",
    ]

    def __init__(self, *args, **kwargs):
        super(Shot, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)

    def create_task(self, content, **data):
        """Creates a new Task with this shot as the parent.

        :param content: task name
        :param data: task data dictionary
        :return: new Task object
        """
        from shotgrid.task import Task

        data.update({"content": content, "entity": self.data})
        results = self.create("Task", data=data)
        return Task(self, results)

    def create_version(self, code, task, **data):
        """Creates a new Version with this shot as the parent.

        :param code: version name
        :param data: version data dictionary
        :return: new Version object
        """
        from shotgrid.version import Version

        data.update({"code": code, "entity": self.data, "sg_task": task.data})
        results = self.create("Version", data=data)
        return Version(self, results)

    def sequence(self):
        """Returns the Sequence object for this Shot."""
        from shotgrid.sequence import Sequence

        return Sequence(None, self.data.sg_sequence)
