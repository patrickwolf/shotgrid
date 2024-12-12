#!/usr/bin/env python

__doc__ = """
Contains Step base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class Step(Entity):
    """Shotgrid Step entity."""

    entity_type = "Step"

    fields = [
        "id",
        "code",
        "description",
        "entity_type",
        "short_name",
        "sg_tank_name",
    ]

    def __init__(self, *args, **kwargs):
        super(Step, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.short_name)

    def create_task(self, content, **data):
        """Creates a new Task with this shot as the parent.

        :param content: task name
        :param data: task data dictionary
        :return: new Task object
        """
        from shotgrid.task import Task

        data.update({"content": content, "step": self.data})
        results = self.create("Task", data=data)
        return Task(self, results)
