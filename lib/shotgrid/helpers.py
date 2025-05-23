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


def remove_keys(data: dict, keys_to_remove: list = [], remove_empty: bool = False, update_in_place: bool = False) -> dict:
    """ 
    Returns a dictionary with specified keys removed. 

    Args:
        data: The original dictionary
        keys_to_remove: List of keys to remove from the dictionary
        update_in_place: If True, modifies the original dictionary and returns it.
                         If False (default), returns a new copy with keys removed.
        remove_empty: If True, removes any keys with empty values (None, "", [], {}, etc.).
                      Default is False.

    Returns:
        A dictionary with the specified keys removed. If update_in_place is True,
        this will be the original dictionary object; otherwise, it will be a copy.
    """
    if not data:
        return {}

    if not keys_to_remove and not remove_empty:
        return data if update_in_place else data.copy()

    # Either use the original dictionary or create a copy
    result = data if update_in_place else data.copy()

    # Remove each key if it exists in the dictionary
    for key in keys_to_remove:
        if key in result:
            del result[key]

    # Remove keys with empty values if requested
    if remove_empty:
        empty_keys = [key for key, value in list(result.items()) if not value]
        for key in empty_keys:
            del result[key]

    return result
