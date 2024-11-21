#!/usr/bin/env python

__doc__ = """
Contains Task base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class Task(Entity):
    """Shotgrid Task entity."""

    entity_type = "Task"

    fields = [
        "id",
        "code",
        "content",
        "name",
        "task_assignees",
        "sg_status_list",
        "versions",
    ]

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.content)

    def get_assignees(self, deep=False):
        """Returns a list of Person objects from shotgrid.

        If deep is False, returned data is shallow, only containing the
        following fields: id, name, and type.

        :param deep: return default Person fields (default False)
        :return: list of Persons assigned to this task
        :raise: gaierror if can't connect to shotgrid.
        """
        from shotgrid.person import Person

        if not deep:
            return [Person(self, r) for r in self.data.task_assignees]

        filters = [["id", "in", [p["id"] for p in self.data.task_assignees]]]
        return self.api().find_entities(Person.entity_type, filters)
