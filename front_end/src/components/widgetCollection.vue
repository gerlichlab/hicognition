<template>
    <div :style="widgetContainerBorder" class="md-elevation-5">
        <md-card :style="cssStyle" ref="collectionCard" class="md-elevation-0" style="z-index: auto;">
            <md-card-header>
                <div class="md-layout">
                    <div class="md-layout-item md-size-30">
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
                    <div class="md-layout-item md-size-55 padding-right">
                        <div class="menu-button">
                            <md-button
                                class="md-icon-button"
                                @click="startDatasetSelection"
                                :disabled="!allowRegionSelection"
                            >
                                <md-icon>menu_open</md-icon>
                                <md-tooltip md-direction="top" md-delay="300"
                                    >Select region for this widget
                                    collection</md-tooltip
                                >
                            </md-button>
                        </div>
                        <div class="menu-button">
                            <md-menu
                                :md-offset-x="50"
                                :md-offset-y="-36"
                                md-size="small"
                                :md-active.sync="showWindowSizeSelection"
                                v-if="allowWindowSizeSelection"
                            >
                                <md-button
                                    class="md-icon-button"
                                    md-menu-trigger
                                >
                                    <md-icon>compare_arrows</md-icon>
                                </md-button>
                                <md-menu-content>
                                    <md-menu-item
                                        v-for="item in pointWindowSizes"
                                        :key="item"
                                        @click="handleWindowSizeSelection(item)"
                                    >
                                        <span class="caption">{{
                                            convertBasePairsToReadable(item)
                                        }}</span>
                                        <md-icon
                                            v-if="selectedWindowSize == item"
                                            >done</md-icon
                                        >
                                    </md-menu-item>
                                </md-menu-content>
                            </md-menu>
                        </div>
                    </div>
                    <div class="md-layout-item md-size-10 padding-left">
                        <div class="menu-button">
                            <md-button
                                @click="deleteCollection"
                                class="
                                    md-icon-button
                                    button-margin
                                    md-primary md-icon-button md-mini
                                "
                            >
                                <md-icon>delete</md-icon>
                            </md-button>
                        </div>
                    </div>
                    <div class="md-layout-item md-size-100 blue-background">
                        <span class="md-caption padding-left">{{
                            dataInfo
                        }}</span>
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
                        <md-icon>chevron_right</md-icon>
                    </md-button>
                </div>
                <div>
                    <md-button
                        class="md-icon-button md-accent md-mini"
                        @click="decreaseColumns"
                        :disabled="!decreaseColumnsAllowed"
                    >
                        <md-icon>chevron_left</md-icon>
                    </md-button>
                </div>
            </div>
        </div>
        <div class="full-width md-layout md-gutter md-alignment-center-center">
            <div class="md-layout-item md-size-40">
                <div class="flex-container-horizontal">
                    <div style="display: inline-block">
                        <md-button
                            class="md-icon-button md-accent md-mini"
                            @click="increaseRows"
                        >
                            <md-icon>expand_more</md-icon>
                        </md-button>
                    </div>
                    <div style="display: inline-block">
                        <md-button
                            class="md-icon-button md-accent md-mini"
                            @click="decreaseRows"
                            :disabled="!decreaseRowsAllowed"
                        >
                            <md-icon>expand_less</md-icon>
                        </md-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import widgetContainer from "./widgetContainer";
import { apiMixin, formattingMixin } from "../mixins";
import { max_array } from "../functions";
import EventBus from "../eventBus";

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
            children: [],
            availableData: {},
            expectSelection: false,
            showWindowSizeSelection: false
        };
    },
    computed: {
        pointWindowSizes: function() {
            return this.windowSizes.filter(el => el != "variable");
        },
        isPointFeature: function() {
            if (this.selectedRegionID) {
                let dataset = this.regions.filter(
                    el => el.id === this.selectedRegionID
                )[0];
                return dataset.sizeType === "Point";
            }
            return false;
        },
        dataInfo: function() {
            if (this.selectedRegionID && this.isPointFeature) {
                return `${
                    this.regions.filter(el => el.id == this.selectedRegionID)[0]
                        .dataset_name
                } | ${this.convertBasePairsToReadable(
                    this.selectedWindowSize
                )}`;
            }
            if (this.selectedRegionID && !this.isPointFeature) {
                return `${
                    this.regions.filter(el => el.id == this.selectedRegionID)[0]
                        .dataset_name
                } | ${this.selectedWindowSize}`;
            }
            return "  ";
        },
        allowRegionSelection: function() {
            return this.regions.length > 0;
        },
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
                background: "rgba(200, 200, 200, 0.2)",
                "margin-right": "10px"
            };
        },
        decreaseRowsAllowed: function() {
            if (this.maxRowNumber == 0) {
                return false;
            }
            var maxRowElements = Math.max(
                ...this.children.map(element => element.rowIndex)
            );
            return this.maxRowNumber > maxRowElements;
        },
        decreaseColumnsAllowed: function() {
            if (this.maxColumnNumber == 0) {
                return false;
            }
            var maxColElements = Math.max(
                ...this.children.map(element => element.colIndex)
            );
            return this.maxColumnNumber > maxColElements;
        },
        allowWindowSizeSelection: function() {
            return (
                this.windowSizes.length > 0 &&
                this.selectedRegionID &&
                this.isPointFeature
            );
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
        handleWindowSizeSelection: function(windowsize) {
            this.selectedWindowSize = windowsize;
        },
        startDatasetSelection: function() {
            this.expectSelection = true;
            let preselection = this.selectedRegionID
                ? [this.selectedRegionID]
                : [];
            EventBus.$emit(
                "show-select-dialog",
                this.regions,
                "bedfile",
                preselection
            );
        },
        registerSelectionEventHandlers: function() {
            EventBus.$on("dataset-selected", this.handleDataSelection);
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion);
        },
        removeSelectionEventHandlers: function() {
            EventBus.$off("dataset-selected", this.handleDataSelection);
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion);
        },
        handleDataSelection: function(id) {
            if (this.expectSelection) {
                this.selectedRegionID = id;
                this.expectSelection = false;
            }
        },
        hanldeSelectionAbortion: function() {
            this.expectSelection = false;
        },
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
        getDatasets: function() {
            this.regions = this.$store.state.datasets.filter(
                element => element.filetype == "bedfile"
            );
        },
        fetchCollections: function() {
            this.fetchData("collections/").then(response => {
                // success, store datasets
                if (response) {
                    this.$store.commit("setCollections", response.data);
                }
            });
        },
        fetchResolutions: function() {
            this.fetchData("resolutions/").then(response => {
                // success, store resolutions
                this.$store.commit("setResolutions", response.data);
                this.windowSizes = Object.keys(response.data);
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
        storeCollectionConfig: function() {
            var payload = {
                id: this.id,
                collectionConfig: {
                    regionID: this.selectedRegionID,
                    availableData: this.availableData,
                    intervalSize: this.selectedWindowSize
                }
            };
            this.$store.commit("compare/setCollectionConfig", payload);
        },
        deleteCollection: function() {
            // call delete of each child
            for (let child of this.children) {
                EventBus.$emit("delete-widget", child.id);
            }
            this.$store.commit("compare/deleteWidgetCollection", this.id);
            // remove dataset from usage counter
            if (this.selectedRegionID) {
                this.$store.commit(
                    "compare/decrement_usage_dataset",
                    this.selectedRegionID
                );
            }
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
            // delete original widget
            EventBus.$emit("delete-widget", sourceWidgetID);
            // update widget data that changed upon drop
            widgetData["id"] = this.getNextID();
            widgetData["rowIndex"] = rowIndex;
            widgetData["colIndex"] = colIndex;
            widgetData["parentID"] = this.id;
            // emit id change event
            EventBus.$emit(
                "widget-id-change",
                sourceWidgetID,
                widgetData["id"]
            );
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
        selectedRegionID: async function(newVal, oldVal) {
            if (!newVal) {
                return;
            }
            // get availability object
            await this.fetchData(`datasets/${newVal}/processedDataMap/`).then(
                response => {
                    // success, store availability object
                    this.availableData = response.data;
                }
            );
            if (
                !this.selectedWindowSize ||
                (this.isPointFeature &&
                    this.selectedWindowSize === "variable") ||
                (!this.isPointFeature && this.selectedWindowSize !== "variable")
            ) {
                // set default -> middle of available windwosizes if point, otherwise variable
                if (this.isPointFeature) {
                    this.selectedWindowSize = this.pointWindowSizes[
                        Math.floor(this.pointWindowSizes.length / 2)
                    ];
                } else {
                    this.selectedWindowSize = "variable";
                }
            } else {
                // both seleted regions and windowsize are defined -> update selected windowsize
                this.storeCollectionConfig();
            }
            // update used_datasets in store -> old dataset is decremented, new one is added
            this.$store.commit("compare/decrement_usage_dataset", oldVal);
            this.$store.commit("compare/increment_usage_dataset", newVal);
        },
        selectedWindowSize: function() {
            this.storeCollectionConfig();
        }
    },
    mounted: function() {
        // register event handlers
        this.registerSelectionEventHandlers();
        // initialize from store
        var collectionData = this.$store.getters[
            "compare/getCollectionProperties"
        ](this.id);
        // set selected dataset and binsize if they are defined
        if (collectionData.collectionConfig) {
            this.selectedRegionID = collectionData.collectionConfig["regionID"];
            this.selectedWindowSize =
                collectionData.collectionConfig["intervalSize"];
            this.availableData =
                collectionData.collectionConfig["availableData"];
        } else {
            // set new collectionConfig if not initialized from store
            let payload = {
                id: this.id,
                collectionConfig: {
                    regionID: undefined,
                    availableData: { pileup: {}, lineprofile: {}, stackup: {} },
                    intervalSize: undefined
                }
            };
            this.$store.commit("compare/setCollectionConfig", payload);
        }
        // set maxrownumber and maxcolumnnumber
        if (collectionData.children) {
            this.maxRowNumber =
                max_array(
                    Object.values(collectionData.children).map(elem => {
                        return elem.rowIndex;
                    })
                ) || 0;
            this.maxColumnNumber =
                max_array(
                    Object.values(collectionData.children).map(elem => {
                        return elem.colIndex;
                    })
                ) || 0;
            // add children
            for (var child of Object.values(collectionData.children)) {
                this.children.push(child);
            }
        }
        // get datasets
        this.getDatasets();
        // get collections
        this.fetchCollections();
        // get resolutions
        if (this.$store.state.resolutions) {
            this.windowSizes = Object.keys(this.$store.getters.getResolutions);
        } else {
            this.fetchResolutions();
        }
    },
    beforeDestroy: function() {
        this.removeSelectionEventHandlers();
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

.flex-container-horizontal {
    display: flex;
    justify-content: center;
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
    height: 90%;
    width: 40px;
    display: inline-block;
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

.blue-background {
    background: var(--md-theme-default-primary);
}
</style>
