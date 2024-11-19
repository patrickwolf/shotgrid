#!/usr/bin/env python

__doc__ = """
Contains Asset base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class Asset(Entity):
    """Shotgrid Asset entity."""

    entity_type = "Asset"

    fields = [
        "id",
        "description",
        "code",
        "sg_status_list",
    ]

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)

    def create_task(self, content, **data):
        """Creates a new Task with this asset as the parent.

        :param content: task name
        :param data: task data dictionary
        :return: new Task object
        """
        from shotgrid.task import Task

        data.update({"content": content, "entity": self.data})
        results = self.create("Task", data=data)
        return Task(self, results)

    def create_version(self, code, task, **data):
        """Creates a new Version with this asset as the parent.

        :param code: version name
        :param data: version data dictionary
        :return: new Version object
        """
        from shotgrid.version import Version

        data.update({"code": code, "entity": self.data, "sg_task": task.data})
        results = self.create("Version", data=data)
        return Version(self, results)
