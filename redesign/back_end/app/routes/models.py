from flask_restx import fields, Namespace

def file_model(ns: Namespace):
    return ns.model('File', {
    "id": fields.Integer(),
    "name": fields.String(),
    "md5": fields.String(),
})