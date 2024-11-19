#!/usr/bin/env python

__doc__ = """
Contains the entity base class.
"""

import socket

from shotgrid.dotdictify import dotdictify
from shotgrid.logger import log


class Entity(object):
    """Entity base class."""

    # must be set on the subclass
    entity_type = None

    # default fields to fetch, override on subclasses
    fields = [
        "id",
        "description",
        "code",
        "name",
        "sg_status_list",
    ]

    def __init__(self, parent, data=None):
        """
        :param parent: shotgrid parent object
        :param data: data dictionary
        """
        self._parent = parent
        self._set_data(data or {})
        if not self.entity_type:
            self.entity_type = self.__class__.__name__

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.name)

    def _set_data(self, data):
        """Sets data.

        :param data: data dictionary
        """
        self.data = dotdictify(data)

    def api(self):
        """Returns Shotgrid api object."""
        parent = self.parent()
        while parent:
            if parent.type() == "Shotgrid":
                return parent
            parent = parent.parent()

    def create(self, entity_type, data):
        """Creates a new entity in shotgrid."""
        data.update({"project": self.get_project().data})
        return self.api().create(entity_type, data)

    def delete(self):
        """Deletes this entity from shotgrid."""
        entity_type = self.__class__.__name__
        return self.api().delete(entity_type, self.id())

    def get_project(self):
        """Returns the project object for this entity."""
        parent = self
        while parent:
            if parent.type() == "Project":
                return parent
            parent = parent.parent()

    def get_tasks(self, content=None, filters=None, fields=None):
        """Returns a list of tasks.

        :param content: sg task name
        :param filters: list of filters to apply to the query
        :param fields: which fields to return (optional)
        :return: list of tasks for this entity
        :raise: gaierror if can't connect to shotgrid
        """
        from shotgrid.task import Task

        fields = fields or Task.fields
        params = [["entity", "is", self.data]]

        if content is not None:
            params.append(["content", "is", content])

        if filters is not None:
            params.extend(filters)

        try:
            results = self.api().find("Task", params, fields=fields)
            tasks = list()
            for r in results:
                tasks.append(Task(self, data=r))
            return tasks

        except socket.gaierror as err:
            log.error(err.message)
            raise

    def get_versions(self, code=None, filters=None, fields=None):
        """Returns a list of versions from shotgrid given a shot and task dictionary.

        :param code: sg version code
        :param filters: additional filters (optional)
        :param fields: which fields to return (optional)
        :return: list of versions for this entity
        :raise: gaierror if can't connect to shotgrid.
        """
        from shotgrid.version import Version

        fields = fields or Version.fields
        params = [["entity", "is", self.data]]

        if code:
            params.append(["code", "is", code])

        if filters is not None:
            params.extend(filters)

        try:
            results = self.api().find("Version", params, fields=fields)
            versions = list()
            for r in results:
                versions.append(Version(self, data=r))
            return versions

        except socket.gaierror as err:
            log.error(err.message)
            raise

    def get_thumb(self):
        """Returns entity thumbnail."""
        raise NotImplementedError

    def id(self):
        """Returns shotgrid entity id."""
        return self.data.id

    def parent(self):
        """Returns the parent of this entity in the query path, e.g.
        using this query path:

            >>> sg.get_projects('abc')[0].get_shots()

        the parent of the Shot objects will be the Project 'abc'. If
        using this query path ::

            >>> sg.get_projects('abc')[0].get_sequences()[0].get_shots()

        then the parent will be a Sequence object.

        The root or top level parent will always be an instance of the
        Shotgrid class.
        """
        return self._parent

    def refetch(self, fields=None):
        """Refetches entity data from shotgrid. Used to update an entity
        after its been updated from another source, or to fetch additional
        fields.

        :param fields: which fields to fetch (optional)
        :raise: gaierror if can't connect to shotgrid.
        """
        filters = [["id", "is", self.id()]]
        results = self.api().find(self.type(), filters, fields or self.fields)
        self.data = dotdictify(results[0])

    def type(self):
        """Returns shotgrid entity type as str."""
        return self.entity_type

    def undelete(self):
        """Restores previously deleted entity from shotgrid."""
        return self.parent().revive(self.type(), self.id())

    def update(self, update_mode=None, **data):
        """Update this entity with new data kwargs.

        :param update_mode: for multi entity fields, dict of entity_type to operation,
            e.g. {'versions': 'add'}. Default is 'set'.
        :param data: field key/value pairs to update
        """
        result = self.api().update(
            self.type(), self.id(), data, multi_entity_update_modes=update_mode
        )
        self.data.update(data)
        return result
