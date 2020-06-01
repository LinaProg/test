import datetime

def serializer(data: dict) -> dict:
    
    result = {}
    for key, value in data.items():
        if type(value) is datetime.datetime or type(value) is datetime.date:
            result[key] = str(value)
        else:
            result[key] = value

    return result