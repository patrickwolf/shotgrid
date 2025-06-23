__doc__ = """
Contains Version base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class PublishedFile(Entity):
    """Shotgrid PublishedFile entity."""

    entity_type = "PublishedFile"

    fields = [
        "id",
        "description",
        "code",
        "name",
        "entity",
        "tags",
        "task",
        "published_file_type",
        "version",
        "path",
        "version_number",
        "sg_ingests"
    ]

    def __init__(self, *args, **kwargs):
        super(PublishedFile, self).__init__(*args, **kwargs)

    # def __repr__(self):
    #     return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)
