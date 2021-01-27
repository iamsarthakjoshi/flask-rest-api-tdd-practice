def is_missing_request_values(body):
    exception_msg = ""
    missing_data_key = [i.capitalize() for i in body if not body[i]]
    if len(missing_data_key) > 0:
        return f"{', '.join(missing_data_key)} are missing."
    return None
