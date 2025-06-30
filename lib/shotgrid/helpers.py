def get_highest_version(version_strings):
    """
    Extract the highest version number from a list of version strings.

    :param version_strings: List of strings containing version numbers in format 'v###'
    :return: The highest version number as an integer

    # Example usage:
    # print(get_highest_version(['STN_6620_povs_OPS_v006', 'STN_6620_ref_OPS_v007', 'STN_6620_comp_OPS_v003']))    
    """
    import re

    # Initialize with lowest possible version
    highest_version = None

    # Pattern to match version numbers (v followed by digits)
    pattern = r'v(\d+)'

    for version_string in version_strings:
        # Search for the pattern in the string
        match = re.search(pattern, version_string)
        if match:
            # Extract the digits and convert to integer
            version_num = int(match.group(1))
            # Update highest version if current is higher
            highest_version = max(highest_version, version_num)

    return highest_version


def list_of_dicts_to_dict(items, key, separator=None) -> dict:
    """
    Convert a list of dictionaries to a dictionary using a specified key.

    If a separator is provided, the value associated with the key must be a
    string, and it will be split by the separator to create multiple entries,
    each pointing to the original item. Leading/trailing whitespace is stripped
    from these split keys.

    Items are skipped if the value obtained for the specified key is falsy
    (e.g., None, empty string, 0, False). Individual keys derived from splitting
    are also skipped if they are falsy after stripping.

    Args:
        items: A list of dictionaries.
        key: The key in the inner dictionaries whose value will be used as
                keys in the output dictionary.
        separator: Optional string to split the key's value by.

    Returns:
        A dictionary mapping processed keys to items.

    Raises:
        TypeError: If a separator is provided and the value for the key
                    is not a string.
        ValueError: If duplicate keys are generated after processing (and are not falsy).
    """
    if not items:
        return {}

    result = {}
    duplicates = set()

    for item in items:
        value_for_key = item.get(key)

        # Skip item if the value for the key is falsy
        if not value_for_key:
            continue

        keys_to_process = []
        if separator:
            if not isinstance(value_for_key, str):
                raise TypeError(
                    f"Value for key '{key}' must be a string when separator is provided. "
                    f"Got type {type(value_for_key).__name__} with value '{value_for_key}'."
                )
            keys_to_process = [k.strip() for k in value_for_key.split(separator)]
        else:
            # If no separator, the value_for_key itself is the key
            keys_to_process = [value_for_key]

        for k_val in keys_to_process:
            # Skip falsy keys (e.g., empty strings resulting from split)
            if not k_val:
                continue

            if k_val in result:
                # Check if it's a true duplicate (same item or different item with same key)
                # The original logic overwrites and flags. This maintains that.
                duplicates.add(k_val)
            result[k_val] = item

    if duplicates:
        # Sort duplicates for consistent error messages.
        # Use key=str for robust sorting if duplicates might contain mixed types.
        sorted_duplicates = sorted(list(duplicates), key=str)
        raise ValueError(f"Duplicate keys found: {sorted_duplicates}")
    return result


def dict_diff(original: dict, updated: dict) -> dict:
    """
    Returns a dictionary containing only the keys that are new or have changed values.

    Args:
        original: The original dictionary
        updated: The updated dictionary to compare against

    Returns:
        A dictionary containing only new keys or keys with changed values
    """
    diff = {}

    # Find new or changed keys
    for key, value in updated.items():
        # If key is new or value has changed
        if key not in original or original[key] != value:
            diff[key] = value

    return diff


def remove_keys(data: dict, keys: list = [], mode: str = "remove", remove_empty: bool = False, update_in_place: bool = False) -> dict:
    """ 
    Returns a dictionary with keys either removed or kept based on the specified mode.

    Args:
        data: The original dictionary
        keys: List of keys to process according to the specified mode
        mode: Either "remove" (default) to remove the specified keys or "keep" to keep only the specified keys
        remove_empty: If True, removes any keys with empty values (None, "", [], {}, etc.).
                      Default is False.
        update_in_place: If True, modifies the original dictionary and returns it.
                         If False (default), returns a new copy with keys processed.

    Returns:
        A dictionary with the specified keys processed. If update_in_place is True,
        this will be the original dictionary object; otherwise, it will be a copy.

    Raises:
        ValueError: If mode is not one of "keep" or "remove"
    """
    if not data:
        return {}

    if mode not in ["keep", "remove"]:
        raise ValueError('Mode must be either "keep" or "remove"')

    if not keys and not remove_empty and mode == "remove":
        return data if update_in_place else data.copy()

    # Either use the original dictionary or create a copy
    result = data if update_in_place else data.copy()

    # Process keys based on mode
    if mode == "remove":
        # Remove each key if it exists in the dictionary
        for key in keys:
            if key in result:
                del result[key]
    else:  # mode == "keep"
        # Keep only the specified keys
        keys_to_remove = [key for key in result if key not in keys]
        for key in keys_to_remove:
            del result[key]

    # Remove keys with empty values if requested
    if remove_empty:
        empty_keys = [key for key, value in list(result.items()) if not value]
        for key in empty_keys:
            del result[key]

    return result
