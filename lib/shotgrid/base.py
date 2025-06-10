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
Contains the entity base class..
"""

import socket
from enum import Enum, auto
from typing import Set, List, Dict, Any, Iterable  # Added List, Dict, Any, Iterable
from shotgrid.dotdictify import dotdictify
import shotgrid.helpers as helpers
from shotgrid.logger import log


class Entity(object):
    """Entity base class."""

    # must be set on the subclass
    entity_type = None
    auto_tag = {'type': 'Tag', 'id': 341}

    # default fields to fetch, override on subclasses
    fields = [
        "id",
        "description",
        "code",
        "name",
        "tags",
        "sg_status_list",
    ]

    def __init__(self, parent: object, data: dict = None):
        """
        :param parent: shotgrid parent object
        :param data: data dictionary
        """
        self._parent = parent
        self._snapshot_data = None  # Initialize snapshot data as None
        self._set_data(data or {})
        if not self.entity_type:
            self.entity_type = self.__class__.__name__

    def __repr__(self):
        # return '<{0} "{1}">'.format(self.__class__.__name__, self.data.name)
        return '<{0} "{1}" ({2})>'.format(self.__class__.__name__, self.uname, self.data.id)

    @property
    def uname(self):
        return self.data.code if self.data.code else self.data.name

    @property
    def code(self):
        return self.data.code

    @code.setter
    def code(self, value):
        self.data.code = value

    @property
    def uname_id(self):
        """Returns the name of the version."""
        return '{0} ({1})'.format(self.uname, self.data.id)

    def _set_data(self, data: dict):
        """Sets data.
        :param data: data dictionary
        """
        self.data = dotdictify(data)

    @property
    def data_id(self):
        """Returns a simplified dict of data useful to use the entity in a filter"""
        minimal_fields = ['id', 'code', 'name', 'content', 'type'
                          ]
        val = {key: getattr(self.data, key) for key in minimal_fields if getattr(self.data, key)}
        # val['uname'] = self.uname_id
        return val

    def api(self):
        """Returns Shotgrid api object."""
        parent = self.parent()
        while parent:
            if parent.type() == "Shotgrid":
                return parent
            parent = parent.parent()

    def save(self):
        """Saves the current entity in shotgrid."""
        if self.id():
            raise ValueError("Cannot save entity with id, use update() instead.")

        data = helpers.remove_keys(self.data, ['id', 'type'])
        data.update({"project": self.get_project().data})
        # Set Pipeline Tag
        if self.auto_tag:
            data.update({'tags': [self.auto_tag]})
        result = self.api().create(self.entity_type, data)
        self._set_data(result)
        return self

    def create(self, entity_type: str, data: dict):
        """Creates a new entity in shotgrid."""
        # Those aren't needed for creating a new entity
        data = helpers.remove_keys(data, ['id', 'type'])
        data.update({"project": self.get_project().data})
        # Set Pipeline Tag
        if self.auto_tag:
            data.update({'tags': [self.auto_tag]})
        return self.api().create(entity_type, data)

    def delete(self):
        """Deletes this entity from shotgrid."""
        entity_type = self.__class__.__name__
        return self.api().delete(entity_type, self.id())

    def get_project(self):
        """Returns the project object for this entity."""
        from shotgrid.project import Project

        parent = self
        while parent:
            if parent.type() == Project.entity_type:
                return parent
            parent = parent.parent()

    def get_tasks(self, content: str = None, filters: list = None, fields: list = None):
        """Returns a list of tasks.

        :param content: sg task name
        :param filters: list of filters to apply to the query
        :param fields: which fields to return (optional)
        :return: list of tasks for this entity
        :raise: gaierror if can't connect to shotgrid
        """
        from shotgrid.step import Step
        from shotgrid.task import Task

        fields = fields or Task.fields

        if self.type() == Step.entity_type:
            params = [["step", "is", self.data]]
        else:
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

    def get_lastest_version_number(self):
        """Returns a list of versions from shotgrid given a shot and task dictionary.

        :param code: sg version code
        :param filters: additional filters (optional)
        :param fields: which fields to return (optional)
        :return: list of versions for this entity
        :raise: gaierror if can't connect to shotgrid.
        """
        from shotgrid.task import Task

        fields = ["code",]

        if self.type() == Task.entity_type:
            filters = [["sg_task", "is", self.data]]
        else:
            filters = [["entity", "is", self.data]]

        try:
            results = self.api().find("Version", filters, fields=fields, limit=3, order=[
                {"field_name": "created_at", "direction": "desc"}])
            versions = [r['code'] for r in results if 'code' in r]
            if not versions:
                return 0
            # Get the highest version number from the list
            return helpers.get_highest_version(versions)
        except socket.gaierror as err:
            log.error(err.message)
            raise

    def get_versions(self, code: str = None, filters: list = None, fields: list = None):
        """Returns a list of versions from shotgrid given a shot and task dictionary.

        :param code: sg version code
        :param filters: additional filters (optional)
        :param fields: which fields to return (optional)
        :return: list of versions for this entity
        :raise: gaierror if can't connect to shotgrid.
        """
        from shotgrid.step import Step
        from shotgrid.version import Version

        fields = fields or Version.fields

        if self.type() == Step.entity_type:
            params = [["sg_task.Task.step", "is", self.data]]
        else:
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

    def _get_published_files(self, code: str = None, id: int = None, filters: list = None, fields: list = None):
        """Returns a list of versions from shotgrid given a shot and task dictionary.

        :param code: sg version code
        :param filters: additional filters (optional)
        :param fields: which fields to return (optional)
        :return: list of versions for this entity
        :raise: gaierror if can't connect to shotgrid.
        """
        from shotgrid.publishedfile import PublishedFile

        fields = fields or PublishedFile.fields

        params = []

        if code:
            params.append(["code", "is", code])

        if filters is not None:
            params.extend(filters)

        return self._get_entities(PublishedFile.entity_type, code, id, params, fields)

    def _get_entities(self, type: str, code: str = None, id: int = None, filters=None, fields: list = None, limit=0):
        """Returns a list of shots from shotgrid for this project.

        :param code: shot code
        :param fields: which fields to return (optional)
        :return: shot list from shotgrid for given project
        :raise: socket.gaierror if can't connect to shotgrid
        """

        fields = fields or self.fields

        if code is not None:
            filters.append(["code", "is", code])

        if id is not None:
            filters.append(["id", "is", id])

        try:
            return self.api().find_entities(type, filters, fields=fields, limit=limit)

        except socket.gaierror as e:
            raise

    def _get_entity(self, type: str, code: str = None, id: int = None, filters=None, fields: list = None):
        """Returns a shot from shotgrid for this project.

        :param id: shot id
        :return: shot object from shotgrid for given project
        :raise: socket.gaierror if can't connect to shotgrid
        """
        entities = self._get_entities(type, code, id, filters, fields, limit=2)
        if len(entities) == 0:
            return None
        if len(entities) == 1:
            return entities[0]
        elif len(entities) > 1:
            raise ValueError(f"Multiple {type} found with code {code}")

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

    def refetch(self, fields: list = None):
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

    def update(self, update_mode: dict = None, **data):
        """Update this entity with new data kwargs.

        :param update_mode: for multi entity fields, dict of entity_type to operation,
            e.g. {'versions': 'add'}. Default is 'set'.
        :param data: field key/value pairs to update
        """
        if not data:
            return self.data

        if self.auto_tag:
            data.update({'tags': [self.auto_tag]})
            if not update_mode:
                update_mode = {'tags': 'set'}
            else:
                update_mode.update({'tags': 'set'})

        # Remove keys that are not in the fields lis
        data = helpers.remove_keys(data, ['id', 'type'])
        result = self.api().update(
            self.type(), self.id(), data, multi_entity_update_modes=update_mode
        )
        self.data.update(result)
        return result

    @property
    def tags(self) -> List[int]:  # Changed return type
        """
        Gets the tag IDs for this entity as a list of unique integers,
        preserving the order from ShotGrid.
        """
        current_sg_tags_list = self.data.get('tags')
        if not isinstance(current_sg_tags_list, list):
            return []

        ids = []
        for tag_dict in current_sg_tags_list:
            if isinstance(tag_dict, dict) and tag_dict.get('type') == 'Tag' and 'id' in tag_dict:
                ids.append(tag_dict['id'])

        # Return unique IDs, preserving order of first appearance
        return ids

    @tags.setter
    def tags(self, value: Set[int]):  # Changed input type to Set[int]
        """
        Sets the tags for this entity from a set of integer IDs.
        Updates self.data.tags to ShotGrid's list of dictionaries format.
        """
        if not isinstance(value, set):
            raise TypeError(f"Tags must be a set of integer IDs. Got {type(value)}.")

        if value and not all(isinstance(item, int) for item in value):
            raise TypeError("All items in the tags set must be integer IDs.")

        self.data.tags = [{'type': 'Tag', 'id': tag_id} for tag_id in value]
    # --------------------------------------------------

    class RetrievalMethod(str, Enum):
        """Methods for retrieving entities from Shotgrid."""
        FIRST = "first"
        ALL = "all"
        UNIQUE = "unique"

    class MissingStrategy(str, Enum):
        """Strategies for handling missing entities."""
        CREATE = "create"
        IGNORE = "ignore"
        RAISE = "raise"

    class EntityType(str, Enum):
        """Supported Shotgrid entity types."""
        PROJECT = "Project"
        ASSET = "Asset"
        SEQUENCE = "Sequence"
        SHOT = "Shot"
        TASK = "Task"
        VERSION = "Version"
        PUBLISHED_FILE = "PublishedFile"
        PLAYLIST = "Playlist"
        YPACKAGE = "CustomEntity07"
        YMEDIA = "CustomEntity06"
        GROUP = "Group"
        PERSON = "Person"

    def load_entity(self, entity_data: dict,
                    retrieval: RetrievalMethod = RetrievalMethod.UNIQUE,
                    missing: MissingStrategy = MissingStrategy.RAISE) -> 'Entity':
        """
        Retrieve or create a Shotgrid entity.

        Args:
            entity_data: Dict with entity data in format {"type": "entity_type", "id": 123} or {"type": "entity_type", "code": "name"}
            parent: Parent entity (Shot or Asset) in Shotgrid entity object format
            retrieval: Method for retrieving entities (FIRST, ALL, UNIQUE)
            missing: Strategy for handling missing entities (CREATE, IGNORE, RAISE)

        Returns:
            The retrieved or created entity, or None if not found and not created
        """
        if not entity_data:
            return None
        parent = self

        # Code field mapping for different entity types
        codes = {
            self.EntityType.PROJECT: "code",
            self.EntityType.ASSET: "code",
            self.EntityType.SEQUENCE: "code",
            self.EntityType.SHOT: "code",
            self.EntityType.TASK: "content",
            self.EntityType.VERSION: "code",
            self.EntityType.PUBLISHED_FILE: "code",
            self.EntityType.PLAYLIST: "code",
            self.EntityType.YPACKAGE: "code",
            self.EntityType.YMEDIA: "code",
            self.EntityType.GROUP: "code",
            self.EntityType.PERSON: "name",
        }

        entity_type = entity_data.get("type")
        entity_id = entity_data.get("id")
        entity_code = entity_data.get("code") if entity_data.get("code") else entity_data.get(codes[entity_type])

        # Validate entity type
        if entity_type not in codes:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        # No code or ID provided
        if not entity_id and not entity_code:
            return None

        # Prepare entity data with the correct field name
        entity_data = entity_data.copy()
        if "code" in entity_data:
            del entity_data["code"]
        entity_data[codes.get(entity_type)] = entity_code

        # If we have an ID, we can create the entity directly
        if entity_id:
            return self.api().create_entity(entity_type, parent, entity_data)

        # Map entity types to their retrieval methods
        retrieval_methods = {
            "Project": "get_projects",
            "Person": "get_persons",
            "Group": "get_groups",
            "Asset": "get_assets",
            "Sequence": "get_sequences",
            "Shot": "get_shots",
            "Task": "get_tasks",
            "Version": "get_versions",
            "Playlist": "get_playlists",
            "Delivery": "get_deliveries",
            "PublishedFile": "get_published_files",
            "CustomEntity07": "get_ypackage",
            "CustomEntity06": "get_ymedia"
        }

        # find_entities
        # Get entity based on type
        entity = None
        get_method = getattr(parent, retrieval_methods.get(entity_type), None)
        if get_method:
            entity = get_method(entity_code)

        if entity:
            if retrieval == self.RetrievalMethod.FIRST:
                return entity[0]
            elif retrieval == self.RetrievalMethod.ALL:
                return entity
            elif retrieval == self.RetrievalMethod.UNIQUE:
                if len(entity) > 1:
                    raise ValueError(f"More than one entity found for {entity_type} with code {entity_code}")
                return entity[0]

        if missing == self.MissingStrategy.CREATE:
            # having the type in here will make it not possible to save later
            # entity_data.pop("type")
            return self.api().create_entity(entity_type, parent, entity_data)
        elif missing == self.MissingStrategy.RAISE:
            raise ValueError(f"Entity not found: {entity_type} with code {entity_code}")
        elif missing == self.MissingStrategy.IGNORE:
            return None

    def snapshot(self):
        """
        Takes a snapshot of the current data state for later comparison.

        Returns:
            self for method chaining
        """
        # Create a deep copy of the current data to avoid reference issues
        import copy
        self._snapshot_data = copy.copy(self.data)
        return self

    def diff(self):
        """
        Returns a dictionary containing only the keys that are new or have changed values
        since the last snapshot was taken.

        Returns:
            A dictionary containing only new keys or keys with changed values

        Raises:
            ValueError: If no snapshot has been taken
        """
        if self._snapshot_data is None:
            return self.data

        # Convert dotdictify objects to regular dictionaries for comparison
        current_data = dict(self.data)
        snapshot_data = dict(self._snapshot_data)

        diff_result = helpers.dict_diff(snapshot_data, current_data)

        return diff_result

    def has_changes(self):
        """
        Checks if there are any changes since the last snapshot.

        Returns:
            True if there are changes, False otherwise

        Raises:
            ValueError: If no snapshot has been taken
        """
        return len(self.diff()) > 0
