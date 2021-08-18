<template>
    <div>
        <div
            :style="cssStyle"
            class="smallMargin md-elevation-1 bg"
            draggable="true"
            @dragstart="handleDragStart"
            @dragend="handleDragEnd"
        >
            <div class="md-layout toolbarheight">
                <div
                    class="md-layout-item md-size-15 padding-left padding-right"
                >
                    <md-menu
                        :md-offset-x="50"
                        :md-offset-y="-36"
                        md-size="auto"
                        :md-active.sync="showDatasetSelection"
                        v-if="allowDatasetSelection"
                        :md-close-on-select="false"
                    >
                        <div class="no-padding-top">
                            <md-button class="md-icon-button" md-menu-trigger>
                                <md-icon>menu_open</md-icon>
                            </md-button>
                        </div>
                        <md-menu-content>
                            <md-menu-item
                                v-for="(item, id) in datasets"
                                :key="id"
                                @click="handleDatasetSelection(id)"
                            >
                                <span class="caption">{{ item.name }}</span>
                                <md-icon v-if="selectedDataset.includes(id)"
                                    >done</md-icon
                                >
                            </md-menu-item>
                        </md-menu-content>
                    </md-menu>
                </div>
                <div
                    class="md-layout-item md-size-60 padding-left padding-right"
                >
                    <md-menu
                        :md-offset-x="50"
                        :md-offset-y="-36"
                        md-size="small"
                        :md-active.sync="showBinSizeSelection"
                        v-if="allowBinsizeSelection"
                    >
                        <div class="no-padding-top">
                            <md-button class="md-icon-button" md-menu-trigger>
                                <md-icon>compare_arrows</md-icon>
                            </md-button>
                        </div>
                        <md-menu-content>
                            <md-menu-item
                                v-for="(item, binsize) in binsizes"
                                :key="binsize"
                                @click="handleBinsizeSelection(binsize)"
                            >
                                <span class="caption">{{
                                    convertBasePairsToReadable(binsize)
                                }}</span>
                                <md-icon v-if="selectedBinsize == binsize"
                                    >done</md-icon
                                >
                            </md-menu-item>
                        </md-menu-content>
                    </md-menu>
                </div>
                <div class="md-layout-item md-size-10">
                    <md-menu
                        :md-offset-x="50"
                        :md-offset-y="-36"
                        md-size="small"
                        :md-active.sync="showMenu"
                    >
                        <div class="no-padding-top">
                            <md-button class="md-icon-button" md-menu-trigger>
                                <md-icon>more_vert</md-icon>
                            </md-button>
                        </div>
                        <md-menu-content>
                            <md-list-item md-expand>
                                <span class="md-body-1">Overlay</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            overlay = 'density';
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Density</span>
                                        <md-icon v-if="overlay == 'density'"
                                            >done</md-icon
                                        >
                                    </md-list-item>
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            overlay = element.index;
                                            showMenu = false;
                                        "
                                        v-for="element in datasetNames"
                                        :key="element.index"
                                    >
                                        <span class="md-body-1">{{
                                            element.name
                                        }}</span>
                                        <md-icon v-if="overlay == element.index"
                                            >done</md-icon
                                        >
                                    </md-list-item>
                                </md-list>
                            </md-list-item>
                        </md-menu-content>
                    </md-menu>
                </div>
                <div class="md-layout-item md-size-10">
                    <div class="no-padding-top padding-right">
                        <md-button
                            @click="deleteWidget"
                            class="md-icon-button md-accent"
                        >
                            <md-icon>delete</md-icon>
                        </md-button>
                    </div>
                </div>
            </div>
            <heatmap
                v-if="showData"
                :stackupID="id"
                :width="visualizationWidth"
                :height="visualizationHeight"
                :stackupData="embeddingData"
                :minHeatmapValue="minHeatmap"
                :maxHeatmapValue="maxHeatmap"
                :minHeatmapRange="minHeatmapRange"
                :maxHeatmapRange="maxHeatmapRange"
                :colormap="colormap"
                :allowValueScaleChange="true"
                @slider-change="handleSliderChange"
                :log="false"
            />
            <div
                v-if="!showData"
                class="md-layout md-alignment-center-center"
                style="height: 89%"
            >
                <md-icon class="md-layout-item md-size-50 md-size-5x"
                    >input</md-icon
                >
            </div>
            <div class="flex-container" v-if="showData">
                <div>
                    <span class="md-caption">{{ message }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { apiMixin, formattingMixin, widgetMixin } from "../../mixins";
import { rectBin, select_column, flatten } from "../../functions";
import heatmap from "../visualizations/heatmap.vue";

export default {
    components: { heatmap },
    name: "Embedding1D",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    computed: {
        colormap: function() {
            return "red";
        },
        message: function() {
            return (
                this.datasets[this.selectedDataset]["name"] +
                " | binsize " +
                this.convertBasePairsToReadable(this.selectedBinsize)
            );
        },
        overlayValues: function() {
            if (this.overlay == "density") {
                return undefined;
            }
            return select_column(
                this.widgetData["features"]["data"],
                this.widgetData["features"]["shape"],
                Number(this.overlay)
            );
        },
        plotBoundaries: function() {
            let minX = Infinity;
            let maxX = -Infinity;
            let minY = Infinity;
            let maxY = -Infinity;
            for (let el of this.points) {
                if (el.x < minX) {
                    minX = el.x;
                }
                if (el.x > maxX) {
                    maxX = el.x;
                }
                if (el.y < minY) {
                    minY = el.y;
                }
                if (el.y > maxY) {
                    maxY = el.y;
                }
            }
            return {
                minX: minX,
                maxX: maxX,
                minY: minY,
                maxY: maxY
            };
        },
        points: function() {
            let embedding = this.widgetData["embedding"]["data"];
            // get x and y coordinates
            let x_vals = [];
            let y_vals = [];
            for (let i = 0; i < embedding.length; i++) {
                if (i % 2 == 0) {
                    x_vals.push(embedding[i]);
                } else {
                    y_vals.push(embedding[i]);
                }
            }
            // construct plot objects
            let points = [];
            for (let j = 0; j < x_vals.length; j++) {
                let densityValue;
                if (this.overlay == "density") {
                    densityValue = 1;
                } else {
                    densityValue = this.overlayValues[j];
                }
                points.push({
                    x: x_vals[j],
                    y: y_vals[j],
                    value: densityValue
                });
            }
            return points;
        },
        embeddingData: function() {
            return {
                data: flatten(
                    rectBin(this.size, this.points, this.plotBoundaries)
                ),
                shape: [this.size, this.size],
                dtype: "float32"
            };
        },
        datasetNames: function() {
            if (this.selectedDataset.length == 0) {
                return [];
            }
            return this.datasets[this.selectedDataset][
                "collection_dataset_names"
            ].map((el, i) => {
                return {
                    name: el,
                    index: String(i)
                };
            });
        }
    },
    methods: {
        blankWidget: function() {
            // removes all information that the user can set in case a certain region/dataset combination is not available
            this.widgetData = undefined;
            this.selectedDataset = [];
            this.selectedBinsize = undefined;
            this.widgetDataRef = undefined;
        },
        handleDatasetSelection: function(id) {
            this.selectedDataset = id;
        },
        handleBinsizeSelection: function(binsize) {
            this.selectedBinsize = binsize;
        },
        toStoreObject: function() {
            // serialize object for storing its state in the store
            return {
                // collection Data is needed if widget is dropped on new collection
                collectionConfig: this.$store.getters[
                    "compare/getCollectionConfig"
                ](this.collectionID),
                colIndex: this.colIndex,
                rowIndex: this.rowIndex,
                id: this.id,
                parentID: this.collectionID,
                dataset: this.selectedDataset,
                datasets: this.datasets,
                binsizes: this.binsizes,
                binsize: this.selectedBinsize,
                widgetDataRef: this.widgetDataRef,
                overlay: this.overlay,
                widgetType: "Embedding1D",
                minHeatmap: this.minHeatmap,
                maxHeatmap: this.maxHeatmap,
                minHeatmapRange: this.minHeatmapRange,
                maxHeatmapRange: this.maxHeatmapRange
            };
        },
        initializeForFirstTime: function(widgetData, collectionData) {
            var data = {
                widgetDataRef: undefined,
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: [],
                selectedBinsize: undefined,
                intervalSize: collectionData["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: {},
                datasets: collectionData["availableData"]["embedding"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                overlay: "density",
                size: 50,
                minHeatmap: undefined,
                maxHeatmap: undefined,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined
            };
            // write properties to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            return data;
        },
        deleteWidget: function() {
            /*
                Needs to be overriden because decrement mutation is different from mixin
            */
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id
            };
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
            // decrement dataset from used dataset in store
            this.$store.commit(
                "compare/decrement_usage_collections",
                this.selectedDataset
            );
        },
        initializeFromStore: function(widgetData, collectionConfig) {
            var widgetDataValues;
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                // deinfe store queries
                var payload = {
                    id: widgetData["widgetDataRef"]
                };
                // get widget data from store
                var widgetDataValues = this.$store.getters[
                    "compare/getWidgetDataEmbedding1d"
                ](payload);
            } else {
                widgetDataValues = undefined;
            }
            // increment dataset usage in store. TODO: these are collections!
            if (widgetData["dataset"]) {
                let datasetId = widgetData["dataset"];
                this.$store.commit(
                    "compare/increment_usage_collections",
                    datasetId
                );
            }
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: collectionConfig["availableData"]["embedding"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                overlay: widgetData["overlay"],
                minHeatmap: widgetData["minHeatmap"],
                maxHeatmap: widgetData["maxHeatmap"],
                minHeatmapRange: widgetData["minHeatmapRange"],
                maxHeatmapRange: widgetData["maxHeatmapRange"],
                size: 50
            };
        },
        handleSliderChange: function(data) {
            this.setColorScale(data);
        },
        setColorScale: function(data) {
            /* 
                sets colorScale based on data array
                containing minPos, maxPos, minRange, maxRange
            */
            this.minHeatmap = data[0];
            this.maxHeatmap = data[1];
            this.minHeatmapRange = data[2];
            this.maxHeatmapRange = data[3];
        },
        resetColorScale: function() {
            /*
                resets colorscale to undefined
            */
            this.minHeatmap = undefined;
            this.maxHeatmap = undefined;
            this.minHeatmapRange = undefined;
            this.maxHeatmapRange = undefined;
        },
        getEmbeddingData: async function(id) {
            // checks whether association data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (
                this.$store.getters["compare/embedding1dDataExists"](
                    queryObject
                )
            ) {
                return this.$store.getters["compare/getWidgetDataEmbedding1d"](
                    queryObject
                );
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(`embeddingIntervalData/${id}/`);
            // save it in store
            var mutationObject = {
                id: id,
                data: response.data
            };
            this.$store.commit(
                "compare/setWidgetDataEmbedding1d",
                mutationObject
            );
            // return it
            return response.data;
        },
        updateData: async function() {
            // reset color scale
            this.resetColorScale();
            // construct data ids to be fecthed
            let selected_id = this.binsizes[this.selectedBinsize];
            // store widget data ref
            this.widgetDataRef = selected_id;
            // fetch data
            this.widgetData = await this.getEmbeddingData(selected_id);
        }
    },
    watch: {
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue) {
                // update availability object
                this.datasets =
                    newValue[this.collectionID]["collectionConfig"][
                        "availableData"
                    ]["embedding"];
                this.intervalSize =
                    newValue[this.collectionID]["collectionConfig"][
                        "intervalSize"
                    ];
            }
        },
        datasets: function(newVal, oldVal) {
            if (
                !newVal ||
                !oldVal ||
                !this.selectedDataset ||
                this.selectedDataset.length == 0
            ) {
                return;
            }
            // check whether there is any data available
            if (!this.datasets[this.selectedDataset]) {
                this.blankWidget();
                return;
            }
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][
                this.intervalSize
            ];
            this.selectedBinsize = this.getCenterOfArray(
                Object.keys(this.binsizes)
            );
            this.updateData();
        },
        intervalSize: function(newVal, oldVal) {
            // if interval size changes, reload data
            if (!newVal || !oldVal || this.selectedDataset.length == 0) {
                return;
            }
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][
                this.intervalSize
            ];
            this.selectedBinsize = this.getCenterOfArray(
                Object.keys(this.binsizes)
            );
            this.updateData();
        },
        selectedDataset: async function(newVal, oldVal) {
            if (!this.selectedDataset || this.selectedDataset.length == 0) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // set binsizes and add default
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][
                this.intervalSize
            ];
            if (!this.selectedBinsize) {
                this.selectedBinsize = this.getCenterOfArray(
                    Object.keys(this.binsizes)
                );
            } else {
                this.updateData();
            }
            // add collections to store for tallying used_collections
            this.$store.commit("compare/decrement_usage_collections", oldVal);
            this.$store.commit("compare/increment_usage_collections", newVal);
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            this.updateData();
        }
    }
};
</script>

<style scoped>
.bg {
    background-color: rgba(211, 211, 211, 0.2);
}

.toolbarheight {
    height: 40px;
}

.flex-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.no-padding-right {
    padding-right: 0px;
}

.padding-right {
    padding-right: 15px;
}

.padding-left {
    padding-left: 10px;
}

.padding-top {
    padding-top: 12px;
}

.no-padding-top {
    padding-top: 0px;
}

.smallMargin {
    margin: 2px;
}

.md-field {
    min-height: 30px;
}
</style>
