from flask_restx import Resource, fields, marshal_with
from app.services.calculations import *
from app.daos import linegraphcalculation_dao, umap1Dcalculation_dao, umap2Dcalculation_dao, heatmapcalculation_dao, stackedlineprofilecalculation_dao, lolacalculation_dao
from flask_restx import Resource, fields, Api, marshal_with, Namespace
from .. import api

class BaseCalcAPI(Resource):
    dao = None
    def get(self):
        # either return all calculations of this type
        # or, if hashes are provided, look for the one calc with this hash
        return self.dao.get_all()
    def post(self):
        # accepts hashes only
        # hashes have to fulfill rule of calculation
        raise NotImplementedError

class BaseCalcIdAPI(Resource):
    dao = None
    def get(self, id):
        return self.dao.get_by_id(id)
    def delete(self, id):
        raise NotImplementedError
    
class BaseCalcHashAPI(Resource):
    dao = None
    def get(self, hash):
        return self.dao.get_by_hash(hash)

calcs = [
    (Namespace('linegraphs', 'Routes to calculate averaged linegraphs.'), linegraphcalculation_dao, linegraph_service),
    (Namespace('1dembeddings', 'Routes to perform clustering of 1D features.'), umap1Dcalculation_dao, umap1D_service),
    (Namespace('2dembeddings', 'Routes to perform clustering of 2D features (heatmaps).'), umap2Dcalculation_dao, umap2D_service),
    (Namespace('lola', 'Routes to perform LOLA analysis.'), lolacalculation_dao, lola_service),
    (Namespace('heatmap_pileups', 'Routes to calculate pileups of HiC-data.'), heatmapcalculation_dao, heatmap_service),
    (Namespace('stackups', 'Routes to calculate stacked up lineprofiles.'), stackedlineprofilecalculation_dao, stackedlineprofile_service),
]

for (namespace, dao, service) in calcs:
    @namespace.route('/')
    class CalcAPI(BaseCalcAPI):
        dao = dao
        service = service
        pass
    
    @namespace.route('/<int:id>')
    class CalcIdAPI(BaseCalcIdAPI):
        dao = dao
        service = service
        pass
    
    @namespace.route('/<string:hash>')
    class CalcHashAPI(BaseCalcHashAPI):
        dao = dao
        service = service
        pass

    api.add_namespace(namespace)

