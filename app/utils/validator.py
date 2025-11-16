from pydantic import validate_email


def is_valid_email(value: str) -> bool:
    try:
        validate_email(value)
        return True
    except:  # noqa
        return False
