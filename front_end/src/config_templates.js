/*
This is a default template
using higlass.io
*/
export var defaultConf = {
    "editable": true,
    "zoomFixed": false,
    "trackSourceServers": [
        "//higlass.io/api/v1",
        "https://resgen.io/api/v1/gt/paper-data"
    ],
    "exportViewUrl": "/api/v1/viewconfs",
    "views": [
        {
            "uid": "aa",
            "initialXDomain": [
                0,
                3100000000
            ],
            "autocompleteSource": "/api/v1/suggest/?d=OHJakQICQD6gTD7skx4EWA&",
            "genomePositionSearchBox": {
                "autocompleteServer": "//higlass.io/api/v1",
                "autocompleteId": "OHJakQICQD6gTD7skx4EWA",
                "chromInfoServer": "//higlass.io/api/v1",
                "chromInfoId": "hg19",
                "visible": true
            },
            "chromInfoPath": "//s3.amazonaws.com/pkerp/data/hg19/chromSizes.tsv",
            "tracks": {
                "top": [
                    {
                        "type": "horizontal-gene-annotations",
                        "height": 60,
                        "tilesetUid": "OHJakQICQD6gTD7skx4EWA",
                        "server": "//higlass.io/api/v1",
                        "position": "top",
                        "uid": "OHJakQICQD6gTD7skx4EWA",
                        "name": "Gene Annotations (hg19)",
                        "options": {
                            "name": "Gene Annotations (hg19)"
                        },
                        "maxWidth": 4294967296,
                        "maxZoom": 22
                    },
                    {
                        "chromInfoPath": "//s3.amazonaws.com/pkerp/data/hg19/chromSizes.tsv",
                        "type": "horizontal-chromosome-labels",
                        "position": "top",
                        "name": "Chromosome Labels (hg19)",
                        "height": 30,
                        "uid": "X4e_1DKiQHmyghDa6lLMVA",
                        "options": {}
                    }
                ],
                "left": [
                    {
                        "type": "vertical-gene-annotations",
                        "width": 60,
                        "tilesetUid": "OHJakQICQD6gTD7skx4EWA",
                        "server": "//higlass.io/api/v1",
                        "position": "left",
                        "name": "Gene Annotations (hg19)",
                        "options": {
                            "labelPosition": "bottomRight",
                            "name": "Gene Annotations (hg19)"
                        },
                        "uid": "dqBTMH78Rn6DeSyDBoAEXw",
                        "maxWidth": 4294967296,
                        "maxZoom": 22
                    },
                    {
                        "chromInfoPath": "//s3.amazonaws.com/pkerp/data/hg19/chromSizes.tsv",
                        "type": "vertical-chromosome-labels",
                        "position": "left",
                        "name": "Chromosome Labels (hg19)",
                        "width": 30,
                        "uid": "RHdQK4IRQ7yJeDmKWb7Pcg",
                        "options": {}
                    }
                ],
                "center": [
                    {
                        "uid": "c1",
                        "type": "combined",
                        "height": 200,
                        "contents": [
                            {
                                "server": "//higlass.io/api/v1",
                                "tilesetUid": "CQMd6V_cRw6iCI_-Unl3PQ",
                                "type": "heatmap",
                                "position": "center",
                                "options": {
                                    "maxZoom": null,
                                    "labelPosition": "bottomRight",
                                    "name": "Rao et al. (2014) GM12878 MboI (allreps) 1kb"
                                },
                                "uid": "GjuZed1ySGW1IzZZqFB9BA",
                                "name": "Rao et al. (2014) GM12878 MboI (allreps) 1kb",
                                "maxWidth": 4194304000,
                                "binsPerDimension": 256,
                                "maxZoom": 14
                            }
                        ],
                        "position": "center",
                        "options": {}
                    }
                ],
                "right": [],
                "bottom": []
            },
            "layout": {
                "w": 12,
                "h": 12,
                "x": 0,
                "y": 0,
                "i": "aa",
                "moved": false,
                "static": false
            }
        }
    ],
    "zoomLocks": {
        "locksByViewUid": {},
        "locksDict": {}
    },
    "locationLocks": {
        "locksByViewUid": {},
        "locksDict": {}
    }
}


/*
This is a template for a local 
Higlass server. The url is injected
during the webpack build process
*/
export var emptyConfLocal = {
    "editable": true,
    "zoomFixed": false,
    "trackSourceServers": [
        process.env.HIGLASS_URL + "/api/v1"
    ],
    "exportViewUrl": "/api/v1/viewconfs",
    "views": [
        {
        "initialXDomain": [
                0,
                3000000000
            ],
            "tracks": {
                "top": [],
                "center": []
            },
            "layout": {
                "w": 20,
                "h": 20,
                "x": 0,
                "y": 0,
                "i": "aa",
                "moved": true,
                "static": true
            }
        }
    ],
    "zoomLocks": {
        "locksByViewUid": {},
        "locksDict": {}
    },
    "locationLocks": {
        "locksByViewUid": {},
        "locksDict": {}
    }
}


/*
This is a template for the top view of a higlass config
*/

export var topView =
    {
        "server": process.env.HIGLASS_URL + "/api/v1",
        "tilesetUid": "",
        "type": "bedlike",
        "options": {
            "fillColor": "blue",
            "axisPositionHorizontal": "right",
            "labelColor": "black",
            "labelPosition": "hidden",
            "labelLeftMargin": 0,
            "labelRightMargin": 0,
            "labelTopMargin": 0,
            "labelBottomMargin": 0,
            "trackBorderWidth": 0,
            "trackBorderColor": "black",
            "valueColumn": null,
            "colorEncoding": false,
            "colorRange": [
                "#000000",
                "#652537",
                "#bf5458",
                "#fba273",
                "#ffffe0"
            ],
            "colorEncodingRange": false,
            "name": ""
        },
        "width": 20,
        "height": 20
    }

/*
Template for coolerview of a higlass config
*/

export var coolerView = {
    "type": "combined",
    "contents": [
        {
            "server": process.env.HIGLASS_URL + "/api/v1",
            "tilesetUid": "",
            "type": "heatmap",
            "options": {
                "backgroundColor": "#eeeeee",
                "labelPosition": "bottomRight",
                "labelLeftMargin": 0,
                "labelRightMargin": 0,
                "labelTopMargin": 0,
                "labelBottomMargin": 0,
                "labelShowResolution": true,
                "colorRange": [
                    "white",
                    "rgba(245,166,35,1.0)",
                    "rgba(208,2,27,1.0)",
                    "black"
                ],
                "colorbarBackgroundColor": "#ffffff",
                "maxZoom": null,
                "colorbarPosition": "topRight",
                "trackBorderWidth": 0,
                "trackBorderColor": "black",
                "heatmapValueScaling": "log",
                "showMousePosition": false,
                "mousePositionColor": "#000000",
                "showTooltip": false,
                "extent": "full",
                "name": "",
                "scaleStartPercent": "0.00000",
                "scaleEndPercent": "1.00000"
            },
            "width": 100,
            "height": 100,
            "transforms": [
                {
                    "name": "ICE",
                    "value": "weight"
                }
            ],
            "resolutions": [
                1000,
                2000,
                4000,
                5000,
                6000,
                8000,
                10000,
                20000,
                50000,
                100000,
                120000,
                150000,
                160000,
                180000,
                200000,
                500000,
                1000000,
                5000000
            ]
        }
    ]
}

/*
This is a template for the bedpeview
*/

export var bedPeView = {
    "server": process.env.HIGLASS_URL + "/api/v1",
    "tilesetUid": "",
    "type": "2d-rectangle-domains",
    "options": {
        "flipDiagonal": "none",
        "labelColor": "black",
        "labelPosition": "hidden",
        "labelLeftMargin": 0,
        "labelRightMargin": 0,
        "labelTopMargin": 0,
        "labelBottomMargin": 0,
        "trackBorderWidth": 0,
        "trackBorderColor": "black",
        "rectangleDomainFillColor": "grey",
        "rectangleDomainStrokeColor": "black",
        "rectangleDomainOpacity": 0.6,
        "minSquareSize": "none",
        "name": ""
    }
}