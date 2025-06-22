__doc__ = """
Contains Version base class.
"""

from shotgrid.base import Entity
from shotgrid.version import Version
from shotgrid.ymedia import YMedia
from shotgrid.logger import log


class YPackage(Entity):
    """Shotgrid Ingest entity."""

    entity_type = "CustomEntity07"

    fields = [
        "id",
        "code",
        "description",
        "sg_status_list",
        "sg_yaction",
        "sg_yissue",
        "sg_ynotes",
        "sg_playlist",
        "sg_ystatus",
        "sg_ysteps",
        "sg_ylogs",
        "sg_ymedia_1",
        "sg_sourcepath",
        "tags"
    ]

    # User Administrated in Shotgrid
    # fields_user = ["sg_status_list", "sg_yaction"]

    def __init__(self, *args, **kwargs):
        super(YPackage, self).__init__(*args, **kwargs)

    # def __repr__(self):
    #     return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)

    def is_version_linked_to_different_package(self, version):
        """
        Check if a Version is linked to a different YPackage than the current one.

        :param version: Version object to check for existing package links
        :return: True if linked to a different package, False otherwise
        :raises ValueError: If version object is invalid or multiple packages are linked
        """
        sg = self.api()

        # Validate version object
        if not version or not isinstance(version, Version):
            raise ValueError("Invalid Version object provided.")

        if not version.id():
            return False

        # Ensure we have the latest version data
        if "sg_ingests" not in version.data:
            version.refetch()

        # TODO: Check if the version has published files linked to YPackage
        # pubfiles = version.get_published_files()
        # [p for p in pubfiles if p.data.get("sg_ypackage")]

        # Get all YMedia items linked to this version
        ymedia_links = version.data.get("sg_ingests", [])
        ymedia_ids = [ymedia.get("id") for ymedia in ymedia_links]

        if not ymedia_ids:
            return False

        # Fetch YMedia items with their linked packages
        ymedia_items = sg.find(
            YMedia.entity_type,
            filters=[['id', 'in', ymedia_ids]],
            fields=['code', 'sg_ypackage']
        )

        # Get unique linked package names
        linked_package_names = {item.get("sg_ypackage", {}).get("name") for item in ymedia_items if item.get("sg_ypackage")}

        if not linked_package_names:
            return False

        if len(linked_package_names) > 1:
            raise ValueError(f"Multiple YMedia items linked to this Version: {linked_package_names}.")

        # Compare with current package code
        current_package_code = self.data.get("code")
        linked_package_name = linked_package_names.pop()

        # Return True if linked to a different package
        return current_package_code != linked_package_name
