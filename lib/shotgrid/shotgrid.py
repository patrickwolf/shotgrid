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

from fpt_api import FPT
__doc__ = """
Contains wrapper class for shotgrid api.
"""

import socket
from enum import Enum, auto
import functools
import shotgun_api3

import shotgrid.helpers as helpers
from shotgrid import config
from shotgrid.asset import Asset
from shotgrid.base import Entity
from shotgrid.logger import log
from shotgrid.person import Person
from shotgrid.group import Group
from shotgrid.playlist import Playlist
from shotgrid.project import Project
from shotgrid.sequence import Sequence
from shotgrid.shot import Shot
from shotgrid.step import Step
from shotgrid.task import Task
from shotgrid.version import Version
from shotgrid.publishedfile import PublishedFile
from shotgrid.ymedia import YMedia
from shotgrid.ypackage import YPackage

# maps entity type string to wrapper class
entity_type_class_map = dict(
    [(cls.entity_type, cls) for cls in Entity.__subclasses__()]
)


class Shotgrid(FPT):
    """
    Shotgrid wrapper base class. Managed connection and starting point for
    all operations, e.g. ::

        >>> sg = Shotgrid()
        >>> projects = sg.get_projects()

    Shotgrid entity hierarchy:

        Shotgrid
            `- Project
                `- Sequence
                    `- Shot
                        |- Version
                        |    `- Movie
                        `- Task
                            `- Person

    """

    def __init__(
        self,
        base_url: str = config.SG_SCRIPT_URL,
        script_name: str = config.SG_SCRIPT_NAME,
        api_key: str = config.SG_SCRIPT_KEY,
        **kwargs,
    ):
        """
        Creates a new Shotgrid object.

        :param base_url: shotgrid base url
        :param script_name: shotgrid script name
        :param api_key: shotgrid api key
        :param kwargs: additional keyword arguments
        """
        super(Shotgrid, self).__init__(base_url, script_name, api_key, **kwargs)
        self.url = base_url
        self.name = script_name
        self.apikey = api_key

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.name)

    def create_project(self, name: str, **data):
        """Creates and returns a new Project entity.

        :param name: project name
        :return: Project entity object
        """
        data.update({"name": name})
        results = self.create("Project", data=data)
        return Project(self, results)

    def find_entities(self, entity_type: str, filters: list, fields: list = None, limit: int = 0):
        """Returns entities matching an entity type and filter list, e.g.
        find an asset with id 1440 ::

            sg.find_entities('Asset', [['id', 'is', 1440]])

        :param entity_type: the entity type string, e.g. Asset
        :param filters: list of filters to apply to the query, e.g. ::
            filters = [['id', 'is', 1440]]
        :returns wrapped entity object
        """
        entities = []
        entity_class = entity_type_class_map.get(entity_type)
        fields = fields or entity_class.fields
        results = self.find(entity_type, filters, fields=fields, limit=limit)
        for r in results:
            entity_type = r.get("type")
            entities.append(entity_class(self, data=r))
        return entities

    def get_projects(self, name: str = None, fields: list = None):
        """Returns a list of Project entities.

        :param name: project name
        :param fields: which fields to return (optional)
        :return: list of projects
        :raise: socket.gaierror if can't connect to shotgrid.
        """

        fields = fields or Project.fields
        params = []

        if name:
            params.append(["name", "is", name])

        try:
            results = self.find("Project", params, fields=fields)
            projects = list()
            for r in results:
                projects.append(Project(self, data=r))
            return projects

        except socket.gaierror as err:
            log.error(err.message)
            raise

    def parent(self):
        """Returns the parent entity of this entity."""
        return None

    def type(self):
        """Returns shotgrid entity type as str."""
        return self.__class__.__name__

    def retire_recent_entities(self, entity_types: list, project_id: int, hours: int = 1):
        """Retires entities that have not been modified in the last n hours.

        :param entity_types: list of entity types to retire
        :param hours: number of hours to check for modification
        """
        if not entity_types:
            raise ValueError("entity_types must not be empty")
        if not project_id:
            raise ValueError("project_id must not be empty")
        if not isinstance(entity_types, list):
            raise ValueError("entity_types must be a list")
        if not isinstance(project_id, int):
            raise ValueError("project_id must be an int")

        filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
            ['created_at', 'in_last', hours, 'HOUR'],
            ['tags', 'is', Entity.auto_tag],
            ['created_by', 'is', {'id': 93, 'name': 'Yeti 1.0', 'type': 'ApiUser'}],
        ]

        items = []
        for entity_type in entity_types:
            items.extend(self.find(entity_type, filters, ['name', 'code', 'content']))

        log.info(f"Retiring {len(items)} entities of type {entity_types} that have been created in the last {hours} hours")
        log.info(items)

        batch_data = []
        for item in items:
            batch_data.append({"request_type": "delete",
                               "entity_type": item["type"],
                               "entity_id": item["id"]})
        self.batch(batch_data)

    @functools.lru_cache(maxsize=None)
    def get_lookup(self, entity_type: str, key_field: str = "code", fields: tuple = None, separator: str = None):
        """
        Get a dictionary of items from Shotgrid using a specified key field.
        Args:   
        entity_type (str): The type of entity to query.
        key_field (str): The field to use as the key in the resulting dictionary.
        fields (list): Optional list of fields to include in the result.
        Returns:
        dict: A dictionary where the keys are the values of the specified key field
            and the values are the corresponding Shotgrid items.
        """
        if not fields:
            fields = [key_field]
        else:
            fields = list(fields)
        if key_field not in fields:
            fields.append(key_field)

        filters = [
            [key_field, "is_not", ""]
        ]
        items = self.find(entity_type, filters, fields=fields)
        result = helpers.list_of_dicts_to_dict(items, key=key_field, separator=separator)
        return result

    @classmethod
    def create_entity(cls, entity_type, parent, data=None):
        """
        Create a new entity of the specified type.

        Args:
            entity_type: String name of the entity type (e.g., "Version", "Task")
            parent: Parent entity to associate with the new entity
            data: Dictionary of initial data for the entity

        Returns:
            A new instance of the specified entity type
        """
        if entity_type not in entity_type_class_map:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        entity_class = entity_type_class_map[entity_type]
        return entity_class(parent, data or {})

    @staticmethod
    def has_id(entity: Entity) -> bool:
        """
        Check if the given entity has an 'id' attribute.

        Args:
            entity: The entity to check

        Returns:
            bool: True if the entity has an 'id', False otherwise
        """
        return entity is not None and hasattr(entity, 'id') and entity.id() is not None

    @staticmethod
    def data_id(entity: Entity) -> dict:
        """
        Check if the given entity has an 'id' attribute.

        Args:
            entity: The entity to check

        Returns:
            bool: True if the entity has an 'id', False otherwise
        """
        if entity is None:
            return None
        elif isinstance(entity, dict) and entity.get('id', None):
            return entity
        elif isinstance(entity, Entity) and entity.id():
            return entity.data_id
