""" fix cross-origin problems. From https://gist.github.com/davidadamojr/465de1f5f66334c91a4c"""
from . import api


@api.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")  # TODO finer control
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response
