def prepare_success_response(data=None) -> dict:
    return dict(success=True, data=data)


def prepare_error_response(errors=None) -> dict:
    return dict(success=False, errors=errors)
