from uuid_extensions import uuid7


def _generate_uuid_v7_with_prefix(prefix: str) -> str:
    """
    Generate a UUID v7 identifier with a custom prefix.

    Args:
        prefix (str): The custom prefix to prepend to the UUID.

    Returns:
        str: The generated UUID v7 identifier with the custom prefix.
    """
    # Generate a UUID v7 identifier
    uuid_v7 = uuid7()

    # Return the UUID with the custom prefix
    return f"{prefix}-{uuid_v7}"


def generate_ref_data_uuid() -> str:
    """
    Generate a UUID v7 identifier with the prefix 'ref'.

    Returns:
        str: The generated UUID v7 identifier with the 'ref' prefix.
    """
    return _generate_uuid_v7_with_prefix("ref")
