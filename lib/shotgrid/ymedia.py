__doc__ = """
Contains Version base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class YMedia(Entity):
    """Shotgrid Ingest entity."""

    entity_type = "CustomEntity06"

    fields = [
        "id",
        "description",
        "code",
        "sg_status_list",
        "sg_submission",
        "sg_srcpath",
        "sg_dstpath",
        "sg_link",
        "sg_task",
        "sg_version",
        "sg_publishedfiletype",
        "sg_publishedfile",
        "sg_playlist",
    ]

    def __init__(self, *args, **kwargs):
        super(Ingest, self).__init__(*args, **kwargs)

    # def __repr__(self):
    #     return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)
