docker run --detach --publish 8888:80 --volume C:\\temp\\Higlass_data:/data --volume C:\\temp\\Higlass_temp:/tmp --name higlass-container higlass/higlass-docker

docker exec higlass-container python higlass-server/manage.py ingest_tileset --filename /tmp/50000kb_binsize_300000_kb_windowsize_insulboundary.bw --filetype bigwig --datatype vector

docker exec higlass-container python higlass-server/manage.py ingest_tileset --filename /tmp/hg19.chromsizes --filetype chromsizes-tsv --datatype chromsizes --coordSystem hg19