"""
Here a baseclass "CalculationService" should be made.
CalculationService:
    create(*data):
        
    calc(Data)





"""
from ..daos import *

class CalculationService:
    def __init__(self, dao):
        self.dao = dao
    
    def get(**hashes):
        # calc composite hash
        # check if hash exists
        # return data
        raise NotImplementedError
    
    def queue_job(**hashes):
        # calc composite hash
        # check if hash exists
        # return data
        raise NotImplementedError
    
    def delete(**hashes):
        # calc composite hash
        # check if hash exists
        # hash calcs from all files hashes added
        raise NotImplementedError
    
    def _calc_hash(**hashes):
        # sum hashes
        # return
        raise NotImplementedError
        
    
    pass

linegraph_service = CalculationService(linegraphcalculation_dao)
umap1D_service = CalculationService(umap1Dcalculation_dao)
umap2D_service = CalculationService(umap2Dcalculation_dao)
lola_service = CalculationService(lolacalculation_dao)
heatmap_service = CalculationService(heatmapcalculation_dao)
stackedlineprofile_service = CalculationService(stackedlineprofilecalculation_dao)

services = {
    'linegraph_service': linegraph_service,
    'umap1d_service': umap1D_service,
    'umap2d_service': umap2D_service,
    'lola_service': lola_service,
    'heatmap_service': heatmap_service,
    'stackedlineprofile_service': stackedlineprofile_service,
}