from enum import Enum, auto
from typing import Optional, Union, Type, TypeVar, Set, List, Dict, Any  # Added Set, List, Dict, Any, Type, TypeVar

# Define a type variable for BaseTagEnum subclasses
T = TypeVar('T', bound='BaseTagEnum')


class BaseTagEnum(Enum):
    """
    Base class for ShotGrid Tag Enums.
    Subclasses should define enum members where the value is the ShotGrid Tag ID.
    e.g., MY_TAG = 123
    """

    @property
    def data_id(self) -> Dict[str, Any]:
        """Return dictionary with type and id for Shotgrid API compatibility."""
        return {'type': 'Tag', 'id': self.value}

    @classmethod
    def from_shotgrid_dict(cls: Type[T], sg_tag_dict: Dict[str, Any]) -> Optional[T]:
        """
        Converts a single ShotGrid tag dictionary to an enum member.
        e.g., {'type': 'Tag', 'id': 123} -> MyTagEnum(123)
        """
        if sg_tag_dict and sg_tag_dict.get('type') == 'Tag' and 'id' in sg_tag_dict:
            try:
                return cls(sg_tag_dict['id'])
            except ValueError:
                # Log if you have a logger instance available, e.g., log.warning(...)
                # print(f"Warning: Tag ID {sg_tag_dict.get('id')} not found in enum {cls.__name__}.")
                return None
        return None

    @classmethod
    def from_shotgrid_list(cls: Type[T], sg_tag_list: Optional[List[Dict[str, Any]]]) -> Set[T]:
        """
        Converts a list of ShotGrid tag dictionaries to a set of enum members.
        e.g., [{'type': 'Tag', 'id': 123}] -> {MyTagEnum(123)}
        """
        if not sg_tag_list:
            return set()

        enum_set = set()
        for sg_tag_dict in sg_tag_list:
            enum_member = cls.from_shotgrid_dict(sg_tag_dict)
            if enum_member:
                enum_set.add(enum_member)
        return enum_set

    @classmethod
    def to_shotgrid_list(cls: Type[T], tag_enum_set: Optional[Set[T]]) -> List[Dict[str, Any]]:
        """
        Converts a set of enum members to a list of ShotGrid tag dictionaries.
        e.g., {MyTagEnum(123)} -> [{'type': 'Tag', 'id': 123}]
        """
        if not tag_enum_set:
            return []
        return [enum_member.data_id for enum_member in tag_enum_set if isinstance(enum_member, cls)]

    @classmethod
    def get_by_value(cls: Type[T], value: int) -> Optional[T]:
        """Get the enum member by its value."""
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def get_by_name(cls: Type[T], name: str, ignore_case: bool = False) -> Optional[T]:
        """Get the enum member by its name."""
        if ignore_case:
            for member in cls:
                if member.name.lower() == name.lower():
                    return member
            return None
        try:
            return cls[name]
        except KeyError:
            return None
