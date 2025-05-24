__doc__ = """
Contains Version base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class YPackage(Entity):
    """Shotgrid Ingest entity."""

    entity_type = "CustomEntity07"

    fields = [
        "id",
        "description",
        "code",
        "sg_status_list",
        "sg_yaction",
        "sg_ynotes",
        "sg_yissue",
        "tags"
    ]

    # User Administrated in Shotgrid
    fields_user = ["sg_status_list", "sg_yaction"]

    def __init__(self, *args, **kwargs):
        super(YPackage, self).__init__(*args, **kwargs)

    # def __repr__(self):
    #     return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)
