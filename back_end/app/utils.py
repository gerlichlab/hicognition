from inflection import camelize, titleize, underscore

class FormatNotSupportedError(Exception):
    """That format is not supported"""
    pass



def _val_to_camel_case(x):
    if not isinstance(x, str):
        return x
    val = camelize(titleize(x).replace(' ', ''))
    return f"{val[0].lower()}{val[1:]}" # hacky
    

def _val_to_snake_case(x):
    if not isinstance(x, str):
        return x
    return underscore(titleize(x).replace(' ',''))

def convert_format(input, format: str) -> dict:
    if not (isinstance(input, list) or isinstance(input, dict)):
        return input
    
    if format == "camelCase":
        formatter = _val_to_camel_case
    elif format == "snake_case": 
        formatter = _val_to_snake_case
    elif format == "human":
        formatter = titleize
    else:
        raise FormatNotSupportedError(f'Format {input} not supported. Supported: camelCase, snake_case, human')
    
    if isinstance(input, list):
        return [convert_format(x, format) for x in input]
    if isinstance(input, dict):
        output_dict = dict()
        for key, value in input.items():
            output_dict[formatter(key)] = convert_format(value, format)
        return output_dict
