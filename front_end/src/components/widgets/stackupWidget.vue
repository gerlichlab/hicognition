<template>
    <div>
        <div
            :style="cssStyle"
            class="smallMargin md-elevation-1 bg"
            draggable="true"
            @dragstart="handleDragStart"
            @dragend="handleDragEnd"
        >
            <div class="md-layout height-71">
                <div
                    class="md-layout-item md-size-35 padding-left padding-right"
                >
                    <md-field class="padding-top">
                        <label class="md-primary">Dataset</label>
                        <md-select
                            v-model="selectedDataset"
                            name="dataset"
                            id="dataset"
                            placeholder="Dataset"
                            :disabled="!allowDatasetSelection"
                        >
                            <md-option
                                v-for="item in datasets"
                                :value="item.id"
                                :key="item.id"
                                >{{ item.dataset_name }}</md-option
                            >
                        </md-select>
                    </md-field>
                </div>
                <div
                    class="md-layout-item md-size-35 padding-left padding-right"
                >
                    <md-field class="padding-top">
                        <label class="md-primary">Binsize</label>
                        <md-select
                            v-model="selectedBinsize"
                            name="binsize"
                            id="binsze"
                            placeholder="Binsize"
                            :disabled="!allowBinsizeSelection"
                        >
                            <md-option
                                v-for="item in binsizes"
                                :value="item.binsize"
                                :key="item.binsize"
                                >{{
                                    convertBasePairsToReadable(item.binsize)
                                }}</md-option
                            >
                        </md-select>
                    </md-field>
                </div>

                <div class="md-layout-item md-size-15">
                    <md-menu
                        md-size="small"
                        :md-offset-x="50"
                        :md-offset-y="-36"
                        :md-active.sync="showMenu"
                    >
                        <div class="padding-top-large padding-right">
                            <md-button
                                class="md-icon-button"
                                md-menu-trigger
                                :disabled="!allowSortOrderSelection"
                            >
                                <md-icon>menu_open</md-icon>
                            </md-button>
                        </div>
                        <md-menu-content>
                            <md-list-item md-expand>
                                <span class="md-body-1">Sort by</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        v-for="item in sortKeys"
                                        :key="item"
                                        @click="
                                            selectedSortOrder = item;
                                            showMenu = false;
                                        "
                                        ><span class="md-body-1">{{
                                            item
                                        }}</span>
                                        <md-icon
                                            v-if="item == selectedSortOrder"
                                            >done</md-icon
                                        >
                                    </md-list-item>
                                    <div class="md-layout">
                                        <div
                                            class="md-layout-item md-size-30 padding-left padding-right"
                                        >
                                            <md-switch v-model="isAscending"
                                                ><span class="md-body-1">{{
                                                    sortDirection
                                                }}</span></md-switch
                                            >
                                        </div>
                                    </div>
                                </md-list>
                            </md-list-item>
                        </md-menu-content>
                    </md-menu>
                </div>
                <div class="md-layout-item md-size-10">
                    <div class="padding-top-large padding-right padding-left">
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
                :width="stackupWidth"
                :height="stackupHeight"
                :sliderHeight="sliderHeight"
                :stackupData="sortedMatrix"
                :minHeatmapValue="minHeatmap"
                :maxHeatmapValue="maxHeatmap"
                colormap="red"
                @slider-change="handleSliderChange"
                :log="false"
            >
            </heatmap>
            <div
                v-if="!showData"
                class="md-layout md-alignment-center-center"
                style="height: 70%;"
            >
                <md-icon class="md-layout-item md-size-50 md-size-5x"
                    >input</md-icon
                >
            </div>
        </div>
    </div>
</template>

<script>
import heatmap from "../visualizations/heatmap";
import { apiMixin, formattingMixin } from "../../mixins";
import {
    group_stackups_by_binsize,
    sort_matrix_by_index,
    sort_matrix_by_center_column
} from "../../functions";
import EventBus from "../../eventBus";

const TOOLBARHEIGHT = 71;

export default {
    name: "stackupWidget",
    mixins: [apiMixin, formattingMixin],
    components: {
        heatmap
    },
    data: function() {
        // get widget data from store for initialization
        return this.initializeWidget();
    },
    props: {
        width: Number,
        height: Number,
        empty: Boolean,
        id: Number,
        collectionID: Number,
        rowIndex: Number,
        colIndex: Number
    },
    computed: {
        stackupHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT) * 0.8);
        },
        stackupWidth: function() {
            return Math.round(this.width * 0.7);
        },
        sliderHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT) * 0.07);
        },
        sortedMatrix: function() {
            if (!this.widgetData) {
                return undefined;
            }
            if (this.selectedSortOrder == "center column") {
                var sorted_matrix = sort_matrix_by_center_column(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            } else {
                var sorted_matrix = sort_matrix_by_index(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.sortorders[this.selectedSortOrder],
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            }
        },
        showData: function() {
            if (this.widgetData) {
                return true;
            }
            return false;
        },
        allowSortOrderSelection: function() {
            if (this.sortorders) {
                return true;
            }
            return false;
        },
        allowDatasetSelection: function() {
            if (this.intervalID) {
                return true;
            }
            return false;
        },
        allowBinsizeSelection: function() {
            return this.binsizes.length != 0;
        },
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            };
        },
        sortDirection: function() {
            if (this.isAscending) {
                return "Ascending";
            }
            return "Descending";
        },
        sortKeys: function() {
            if (this.sortorders) {
                return Object.keys(this.sortorders);
            }
            return {};
        }
    },
    methods: {
        serializeWidget: function() {
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
        },
        handleSliderChange: function(data) {
            this.minHeatmap = data[0];
            this.maxHeatmap = data[1];
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
                widgetType: "Stackup",
                minHeatmap: this.minHeatmap,
                maxHeatmap: this.maxHeatmap,
                selectedSortOrder: this.selectedSortOrder,
                sortorders: this.sortorders,
                isAscending: this.isAscending
            };
        },
        deleteWidget: function() {
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id
            };
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
            // decrement dataset from used dataset in store
            this.$store.commit(
                "compare/decrement_usage_dataset",
                this.selectedDataset
            );
        },
        handleDragStart: function(e) {
            // commit to store once drag starts
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            // create data transfer object
            e.dataTransfer.setData("widget-id", this.id);
            e.dataTransfer.setData("collection-id", this.collectionID);
            // set dragimage. Dragimage dom element needs to be present before it can be passed
            // to setDragImage. Div is positioned outside of visible area for this
            this.dragImage = document.createElement("div");
            this.dragImage.style.backgroundColor = "grey";
            this.dragImage.style.height = `${this.height}px`;
            this.dragImage.style.width = `${this.width}px`;
            this.dragImage.style.position = "absolute";
            this.dragImage.style.top = `-${this.width}px`; // positioning outside of visible area
            document.body.appendChild(this.dragImage);
            e.dataTransfer.setDragImage(
                this.dragImage,
                this.height / 2,
                this.width / 2
            );
        },
        handleDragEnd: function(e) {
            // remove dragImage from document
            if (this.dragImage) {
                this.dragImage.remove();
            }
        },
        sameCollectionConfig: function(newCollectionData, oldCollectionData) {
            if (!oldCollectionData) {
                // no old data -> the widget needs to be freshly initialized
                return false;
            }
            if (
                newCollectionData["intervalID"] !=
                oldCollectionData["intervalID"]
            ) {
                return false;
            }
            return true;
        },
        initializeForFirstTime: function(widgetData, collectionData) {
            var data = {
                widgetDataRef: undefined,
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalID: collectionData["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: this.$store.getters.getBigwigsDirty,
                minHeatmap: undefined,
                maxHeatmap: undefined,
                selectedSortOrder: "center column",
                sortorders: undefined,
                isAscending: true,
                showMenu: false
            };
            // write properties to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            return data;
        },
        initializeAtNewCollection: function(widgetData, collectionConfig) {
            return {
                widgetDataRef: undefined,
                minHeatmap: undefined,
                maxHeatmap: undefined,
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalID: collectionConfig["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                selectedSortOrder: "center column",
                datasets: this.$store.getters.getBigwigsDirty,
                sortorders: undefined,
                isAscending: true,
                showMenu: false
            };
        },
        initializeAtSameCollection: function(widgetData, collectionConfig) {
            var widgetDataValues;
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                var widgetDataRef = widgetData["widgetDataRef"];
                // deinfe store queries
                var querydata = {
                    id: widgetDataRef
                };
                // get widget data from store
                widgetDataValues = this.$store.getters[
                    "compare/getWidgetDataStackup"
                ](querydata);
            } else {
                widgetDataValues = undefined;
            }
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedSortOrder: widgetData["selectedSortOrder"],
                minHeatmap: widgetData["minHeatmap"],
                maxHeatmap: widgetData["maxHeatmap"],
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalID: collectionConfig["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: this.$store.getters.getBigwigsDirty,
                sortorders: widgetData["sortorders"],
                isAscending: widgetData["isAscending"],
                showMenu: false
            };
        },
        initializeWidget: function() {
            // initialize widget from store
            var queryObject = {
                parentID: this.collectionID,
                id: this.id
            };
            var widgetData = this.$store.getters["compare/getWidgetProperties"](
                queryObject
            );
            // the collection config at the current collection
            var collectionConfig = this.$store.getters[
                "compare/getCollectionConfig"
            ](this.collectionID);
            // the collection config the widget comes from
            var oldCollectionConfig = widgetData["collectionConfig"];
            if (!oldCollectionConfig) {
                return this.initializeForFirstTime(
                    widgetData,
                    collectionConfig
                );
            }
            if (
                this.sameCollectionConfig(collectionConfig, oldCollectionConfig)
            ) {
                return this.initializeAtSameCollection(
                    widgetData,
                    collectionConfig
                );
            }
            return this.initializeAtNewCollection(widgetData, collectionConfig);
        },
        getStackupData: async function(id) {
            // checks whether pileup data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (this.$store.getters["compare/stackupExists"](queryObject)) {
                return this.$store.getters["compare/getWidgetDataStackup"](
                    queryObject
                );
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(
                `individualIntervalData/${id}/`
            );
            var piling_data = response.data;
            // save it in store
            var mutationObject = {
                id: id,
                data: piling_data
            };
            this.$store.commit("compare/setWidgetDataStackup", mutationObject);
            // return it
            return piling_data;
        }
    },
    watch: {
        "$store.state.datasets": function() {
            // updates datasets if they change -> get coolers that may be in the status of processing
            this.datasets = this.$store.getters.getBigwigsDirty;
        },
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue) {
                // check if collecitonConfig is defined
                if ("collectionConfig" in newValue[this.collectionID]) {
                    // check if intervals has changed
                    var newEntry =
                        newValue[this.collectionID]["collectionConfig"][
                            "intervalID"
                        ];
                    if (newEntry != this.intervalID) {
                        this.intervalID = newEntry;
                        this.selectedBinsize = undefined;
                        this.selectedDataset = undefined;
                        this.widgetData = undefined;
                        this.binsizes = [];
                    }
                }
            }
        },
        selectedDataset: function(newVal, oldVal) {
            if (!this.selectedDataset) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // fetch binsizes for the current combination of dataset and intervals
            this.fetchData(
                `individualIntervalData/?dataset_id=${this.selectedDataset}&intervals_id=${this.intervalID}`
            ).then(response => {
                // update binsizes to show and group iccf/obsExp data under one binsize
                this.binsizes = group_stackups_by_binsize(response.data);
            });
            // add dataset to store for tallying used_dataset
            this.$store.commit("compare/decrement_usage_dataset", oldVal);
            this.$store.commit("compare/increment_usage_dataset", newVal);
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            // fetch widget data
            var stackup_id = this.binsizes[this.selectedBinsize]["id"];
            this.widgetDataRef = stackup_id;
            var data = await this.getStackupData(stackup_id);
            this.widgetData = data;
            // fetch metadata
            var response = await this.fetchData(
                `individualIntervalData/${stackup_id}/metadatasmall`
            );
            this.sortorders = response.data;
            // add by center column
            this.sortorders["center column"] = {};
        }
    },
    mounted: function() {
        EventBus.$on("serialize-widgets", this.serializeWidget);
    }
};
</script>

<style scoped>
.bg {
    background-color: rgba(211, 211, 211, 0.2);
}

.height-71 {
    height: 71px;
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

.padding-top-large {
    padding-top: 17px;
}

.smallMargin {
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 2px;
    margin-bottom: 1px;
}

.md-field {
    min-height: 30px;
}
</style>
