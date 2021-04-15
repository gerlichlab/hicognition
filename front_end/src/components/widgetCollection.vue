<template>
    <div
        :style="widgetContainerBorder"
        class="md-elevation-5"
    >
        <md-card :style="cssStyle" ref="collectionCard" class="md-elevation-0">
            <md-card-header>
                <div class="md-layout">
                    <div class="md-layout-item md-size-30 padding-right">
                        <div class="menu-button">
                            <md-button
                                @click="handleZoomIn"
                                class="md-icon-button"
                            >
                                <md-icon>zoom_in</md-icon>
                            </md-button>
                        </div>
                        <div class="menu-button">
                            <md-button
                                @click="handleZoomOut"
                                class="md-icon-button"
                                :disabled="blockZoomOut"
                            >
                                <md-icon>zoom_out</md-icon>
                            </md-button>
                        </div>
                    </div>
                    <div class="md-layout-item md-size-30 padding-right">
                        <md-field class="padding-top">
                            <label class="md-primary" for="region"
                                >Region</label
                            >
                            <md-select
                                v-model="selectedRegionID"
                                name="region"
                                id="region"
                                placeholder="Region"
                            >
                                <md-option
                                    v-for="item in regions"
                                    :value="item.id"
                                    :key="item.id"
                                    >{{ item.dataset_name }}</md-option
                                >
                            </md-select>
                        </md-field>
                    </div>
                    <div class="md-layout-item md-size-25">
                        <md-field class="padding-top">
                            <label class="md-primary" for="Size">Size</label>
                            <md-select
                                v-model="selectedWindowSize"
                                name="size"
                                id="size"
                                placeholder="Size"
                                :disabled="!windowSizesAvailable"
                            >
                                <md-option
                                    v-for="item in windowSizes"
                                    :value="item.id"
                                    :key="item.id"
                                    >{{
                                        convertBasePairsToReadable(
                                            item.windowsize
                                        )
                                    }}</md-option
                                >
                            </md-select>
                        </md-field>
                    </div>
                    <div class="md-layout-item md-size-10 padding-left">
                        <div class="menu-button">
                            <md-button
                                @click="deleteCollection"
                                class="md-icon-button button-margin md-primary md-icon-button md-mini"
                            >
                                <md-icon>delete</md-icon>
                            </md-button>
                        </div>
                    </div>
                </div>
                <md-divider></md-divider>
            </md-card-header>
            <md-card-content class="nomargin">
                <widgetContainer
                    class="inline"
                    v-for="item in flattenedElements"
                    :key="item.id"
                    :height="item.height"
                    :width="item.width"
                    :empty="item.empty"
                    :id="item.id"
                    :collectionID="id"
                    :rowIndex="item.rowIndex"
                    :colIndex="item.colIndex"
                    @widgetDrop="handleWidgetDrop"
                />
            </md-card-content>
        </md-card>
        <div class="column-button-container">
            <div class="flex-container">
                <div>
                    <md-button
                        class="md-icon-button md-accent md-mini"
                        @click="increaseColumns"
                    >
                        <md-icon>add</md-icon>
                    </md-button>
                </div>
                <div>
                    <md-button
                        class="md-icon-button md-accent md-mini"
                        @click="decreaseColumns"
                        :disabled="!decreaseColumnsAllowed"
                    >
                        <md-icon>remove</md-icon>
                    </md-button>
                </div>
            </div>
        </div>
        <div class="full-width md-layout md-gutter md-alignment-center-center">
            <div class="md-layout-item md-size-25">
                <md-button
                    class="md-icon-button md-accent md-mini"
                    @click="increaseRows"
                >
                    <md-icon>add</md-icon>
                </md-button>
            </div>
            <div class="md-layout-item md-size-25">
                <md-button
                    class="md-icon-button md-accent md-mini"
                    @click="decreaseRows"
                    :disabled="!decreaseRowsAllowed"
                >
                    <md-icon>remove</md-icon>
                </md-button>
            </div>
        </div>
    </div>
</template>

<script>
import widgetContainer from "./widgetContainer";
import { apiMixin, formattingMixin } from "../mixins";

export default {
    name: "widgetCollection",
    mixins: [apiMixin, formattingMixin],
    props: {
        id: Number
    },
    components: {
        widgetContainer
    },
    data: function() {
        return {
            regions: [],
            windowSizes: [],
            selectedRegionID: null,
            selectedWindowSize: null,
            marginSizeWidth: 4,
            marginSizeHeight: 10,
            paddingWidth: 11,
            paddingHeight: 80,
            baseWidth: 350,
            baseHeight: 350,
            maxRowNumber: 0,
            maxColumnNumber: 0,
            children: []
        };
    },
    computed: {
        widgetContainerBorder: function() {
            return {
                width: `${this.collectionWidth +
                    this.paddingWidth +
                    40 +
                    (this.maxColumnNumber + 1) * this.marginSizeWidth}px`,
                height: `${this.collectionHeight +
                    this.paddingHeight +
                    40 +
                    (this.maxRowNumber + 1) * this.marginSizeHeight}px`,
                background: "rgba(75, 75, 75, 0.1)",
                "margin-right": "10px"
            };
        },
        decreaseRowsAllowed: function(){
            var maxRowElements = Math.max(
                ...this.children.map(element => element.rowIndex)
            );
            return this.maxRowNumber > maxRowElements
        },
        decreaseColumnsAllowed: function() {
            var maxColElements = Math.max(
                ...this.children.map(element => element.colIndex)
            );
            return this.maxColumnNumber > maxColElements
        },
        windowSizesAvailable: function() {
            if (this.windowSizes.length != 0) {
                return true;
            }
            return false;
        },
        blockZoomOut: function() {
            if (this.baseWidth <= 350) {
                return true;
            }
            return false;
        },
        collectionHeight: function() {
            return (this.maxRowNumber + 1) * this.baseHeight;
        },
        collectionWidth: function() {
            return (this.maxColumnNumber + 1) * this.baseWidth;
        },
        elementMatrix: function() {
            // creates element matrix from children filled up with empty elements
            var matrix = [];
            // create empty matrix
            for (var rowIndex = 0; rowIndex <= this.maxRowNumber; rowIndex++) {
                var emptyRow = [];
                for (
                    var colIndex = 0;
                    colIndex <= this.maxColumnNumber;
                    colIndex++
                ) {
                    emptyRow[colIndex] = {
                        id: this.getNextID(),
                        height: this.baseHeight,
                        width: this.baseWidth,
                        empty: true,
                        rowIndex: rowIndex,
                        colIndex: colIndex,
                        parentID: this.id
                    };
                }
                matrix.push(emptyRow);
            }
            // fill in children
            for (var child of this.children) {
                matrix[child.rowIndex][child.colIndex] = {
                    id: child.id,
                    height: this.baseHeight,
                    width: this.baseWidth,
                    empty: false,
                    rowIndex: child.rowIndex,
                    colIndex: child.colIndex,
                    text: child.text,
                    parentID: this.id
                };
            }
            return matrix;
        },
        flattenedElements: function() {
            // gives a flattened representation of elements
            var output = [];
            for (var row of this.elementMatrix) {
                for (var element of row) {
                    output.push(element);
                }
            }
            return output;
        },
        cssStyle: function() {
            return {
                height: `${this.collectionHeight +
                    this.paddingHeight +
                    (this.maxRowNumber + 1) * this.marginSizeHeight}px`,
                width: `${this.collectionWidth +
                    this.paddingWidth +
                    (this.maxColumnNumber + 1) * this.marginSizeWidth}px`,
                "margin-left": "0px",
                "margin-right": "0px",
                float: "left"
            };
        }
    },
    methods: {
        increaseRows: function() {
            this.maxRowNumber = this.maxRowNumber + 1;
        },
        decreaseRows: function() {
            this.maxRowNumber = this.maxRowNumber - 1;
        },
        increaseColumns: function() {
            this.maxColumnNumber = this.maxColumnNumber + 1;
        },
        decreaseColumns: function() {
            this.maxColumnNumber = this.maxColumnNumber - 1;
        },
        getNextID: function() {
            return Math.floor(Math.random() * 1000000000);
        },
        fetchDatasets: function() {
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                this.$store.commit("setDatasets", response.data);
                // update datasets
                this.regions = response.data.filter(
                    element => element.filetype == "bedfile"
                );
            });
        },
        handleZoomIn: function() {
            this.baseWidth += 50;
            this.baseHeight += 50;
        },
        handleZoomOut: function() {
            this.baseWidth -= 50;
            this.baseHeight -= 50;
        },
        deleteCollection: function() {
            this.$store.commit("compare/deleteWidgetCollection", this.id);
        },
        handleWidgetDrop: function(
            sourceColletionID,
            sourceWidgetID,
            rowIndex,
            colIndex
        ) {
            // oupdate widget data that are managed by collection: ID, colIndex, rowIndex, parentID
            var queryObject = {
                parentID: sourceColletionID,
                id: sourceWidgetID
            };
            var widgetData = this.$store.getters["compare/getWidgetProperties"](
                queryObject
            );
            // delete original widget in store
            this.$store.commit("compare/deleteWidget", queryObject);
            // update widget data that changed upon drop
            widgetData["id"] = this.getNextID();
            widgetData["rowIndex"] = rowIndex;
            widgetData["colIndex"] = colIndex;
            widgetData["parentID"] = this.id;
            // update changed data in store
            this.$store.commit("compare/setWidget", widgetData);
        }
    },
    watch: {
        // watch for changes in store
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue, oldValue) {
                // check if own entry changed
                var newEntry = Object.assign({}, newValue[this.id]);
                var oldEntry = Object.assign({}, oldValue[this.id]);
                if (newEntry != oldEntry) {
                    // entry changed, assign new child-widgets to draw
                    this.children = [];
                    for (var child of Object.values(newEntry.children)) {
                        this.children.push(child);
                    }
                }
            }
        },
        selectedRegionID: function() {
            // fetch intervals and assing to windowsizes
            this.fetchData(`datasets/${this.selectedRegionID}/intervals/`).then(
                response => {
                    this.windowSizes = response.data;
                }
            );
            // clear region
            this.selectedWindowSize = null;
        },
        selectedWindowSize: function() {
            // set new intervals
            var payload = {
                id: this.id,
                collectionConfig: { intervalID: this.selectedWindowSize }
            };
            this.$store.commit("compare/setCollectionConfig", payload);
        }
    },
    mounted: function() {
        // initialize from store
        var collectionData = this.$store.getters[
            "compare/getCollectionProperties"
        ](this.id);
        for (var child of Object.values(collectionData.children)) {
            this.children.push(child);
        }
        // get datasets
        this.fetchDatasets();
    }
};
</script>

<style scoped>
.padding-top {
    padding-top: 10px;
}

.padding-right {
    padding-right: 10px;
}

.padding-left {
    padding-left: 10px;
}

.padding-bottom {
    padding-bottom: 10px;
}

.flex-container {
    display: flex;
    justify-content: center;
    flex-direction: column;
    height: 100%;
    align-items: center;
}

.full-width {
    width: 100%;
}

.center {
    justify-content: center;
}

.column-button-container {
    height:90%;
    width:40px;
    display:inline-block;
}

.inline {
    display: inline-block;
    vertical-align: top;
}

.menu-button {
    padding-top: 10px;
    padding-right: 0px;
    padding-left: 0px;
    display: inline-block;
    vertical-align: top;
}

.md-card-header {
    padding: 0px;
}

.halfSize {
    width: 50vw;
    height: 50vh;
}

.nomargin {
    margin: 0px;
    padding: 5px;
}

.md-field {
    min-height: 30px;
}
</style>
