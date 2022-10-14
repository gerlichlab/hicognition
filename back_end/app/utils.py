from enum import Enum
from inflection import camelize, titleize, underscore

class Format(Enum):
    SNAKE_CASE = 1
    CAMELCASE = 2
    HUMAN_READABLE = 3

    
class FormatNotSupportedError(Exception):
    """That format is not supported"""
    pass

def _val_to_camel_case(x):
    if not isinstance(x, str):
        return x
    val = camelize(titleize(x).replace(' ', ''))
    if len(val) > 1:
        return f"{val[0].lower()}{val[1:]}"
    elif len(val) == 1:
        return val.lower()
    else:
        return val
    

def _val_to_snake_case(x):
    if not isinstance(x, str):
        return x
    return underscore(titleize(x).replace(' ',''))

def convert_format(input, format):    
    if format == Format.CAMELCASE:
        formatter = _val_to_camel_case
    elif format == Format.SNAKE_CASE: 
        formatter = _val_to_snake_case
    elif format == Format.HUMAN_READABLE:
        formatter = titleize
    else:
        raise FormatNotSupportedError(f'Format {input} not supported. Supported: camelCase, snake_case, human')

    if isinstance(input, str):
        return formatter(input)
    elif isinstance(input, list):
        return [convert_format(x, format) for x in input]
    elif isinstance(input, dict):
        output_dict = dict()
        for key, value in input.items():
            output_dict[formatter(key)] = convert_format(value, format)
        return output_dict
    else:
        return input
