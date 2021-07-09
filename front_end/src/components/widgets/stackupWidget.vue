<template>
    <div
        @click="handleWidgetSelection"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
    >
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
                                v-for="(item, id) in datasets"
                                :value="id"
                                :key="id"
                                >{{ item.name }}</md-option
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
                                v-for="(item, binsize) in binsizes"
                                :value="binsize"
                                :key="binsize"
                                >{{
                                    convertBasePairsToReadable(binsize)
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
                                        :disabled="sortOrderRecipient"
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
                                            <md-switch
                                                v-model="isAscending"
                                                :disabled="sortOrderRecipient"
                                                ><span class="md-body-1">{{
                                                    sortDirection
                                                }}</span></md-switch
                                            >
                                        </div>
                                    </div>
                                </md-list>
                            </md-list-item>
                            <md-list-item md-expand>
                                <span class="md-body-1">Share</span>
                                <md-list slot="md-expand">
                                    <md-list-item
                                        @click="handleStartSortOrderShare"
                                        :disabled="
                                            sortOrderRecipient ||
                                                this.sortOrderRecipients > 0
                                        "
                                        ><span class="md-body-1"
                                            >Take sort order from</span
                                        >
                                    </md-list-item>
                                    <md-list-item
                                        @click="handleStopSortOrderShare"
                                        :disabled="!sortOrderRecipient"
                                    >
                                        <span class="md-body-1"
                                            >Release sort order</span
                                        >
                                    </md-list-item>
                                    <md-list-item
                                        @click="handleStartValueScaleShare"
                                        :disabled="
                                            valueScaleRecipient ||
                                                this.valueScaleRecipients > 0
                                        "
                                        ><span class="md-body-1"
                                            >Take value scale from</span
                                        >
                                    </md-list-item>
                                    <md-list-item
                                        @click="handleStopValueScaleShare"
                                        :disabled="!valueScaleRecipient"
                                    >
                                        <span class="md-body-1"
                                            >Release value scale</span
                                        >
                                    </md-list-item>
                                </md-list>
                            </md-list-item>
                        </md-menu-content>
                    </md-menu>
                </div>
                <div class="md-layout-item md-size-10">
                    <div class="padding-top-large padding-right padding-left">
                        <md-button
                            @click="handleWidgetDeletion"
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
                :sliderHeight="sliderHeight"
                :stackupData="sortedMatrix"
                :minHeatmapValue="minHeatmap"
                :maxHeatmapValue="maxHeatmap"
                :minHeatmapRange="minHeatmapRange"
                :maxHeatmapRange="maxHeatmapRange"
                :colormap="colormap"
                :valueScaleColor="valueScaleColor"
                :valueScaleBorder="valueScaleBorder"
                :allowValueScaleChange="allowValueScaleChange"
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
import {
    apiMixin,
    formattingMixin,
    widgetMixin,
    sortOrderMixin,
    valueScaleSharingMixin
} from "../../mixins";
import EventBus from "../../eventBus";
import * as seedrandom from "seedrandom";

export default {
    name: "stackupWidget",
    mixins: [
        apiMixin,
        formattingMixin,
        widgetMixin,
        valueScaleSharingMixin,
        sortOrderMixin,
    ],
    components: {
        heatmap
    },
    computed: {
        colormap: function() {
            return "red";
        }
    },
    methods: {
        handleMouseEnter: function() {
            if (
                this.allowSortOrderTargetSelection ||
                this.allowValueScaleTargetSelection
            ) {
                this.showSelection = true;
            }
        },
        handleMouseLeave: function() {
            if (
                this.allowSortOrderTargetSelection ||
                this.allowValueScaleTargetSelection
            ) {
                this.showSelection = false;
            }
        },
        handleWidgetSortOrderSelection: function() {
            if (this.sortOrderRecipients == 0) {
                this.manageColorUpdate();
            }
            EventBus.$emit(
                "select-sort-order-end",
                this.id,
                this.constructSortOrder(),
                this.isAscending,
                this.sortOrderColor
            );
            this.sortOrderRecipients += 1;
            this.showSelection = false;
        },
        handleWidgetValueScaleSelection: function() {
            if (this.valueScaleRecipients == 0) {
                this.manageValueScaleColorUpdate();
            }
            EventBus.$emit(
                "select-value-scale-end",
                this.id,
                this.minHeatmap,
                this.maxHeatmap,
                this.valueScaleColor,
                this.colormap,
                this.minHeatmapRange,
                this.maxHeatmapRange
            );
            this.valueScaleRecipients += 1;
            this.showSelection = false;
        },
        handleWidgetSelection: function() {
            if (this.allowSortOrderTargetSelection) {
                this.handleWidgetSortOrderSelection();
            } else if (this.allowValueScaleTargetSelection) {
                this.handleWidgetValueScaleSelection();
            }
        },
        handleSliderChange: function(data) {
            this.setColorScale(data);
            this.broadcastValueScaleUpdate();
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
                isAscending: this.isAscending,
                expectingSortOrder: false,
                sortOrderSelectionState: false,
                showSelection: false,
                sortOrderRecipient: this.sortOrderRecipient,
                sortOrderRecipients: this.sortOrderRecipients,
                sortOrderTargetID: this.sortOrderTargetID,
                sortOrderColor: this.sortOrderColor,
                valueScaleRecipient: this.valueScaleRecipient,
                valueScaleRecipients: this.valueScaleRecipients,
                valueScaleTargetID: this.valueScaleTargetID,
                valueScaleColor: this.valueScaleColor,
                minHeatmapRange: this.minHeatmapRange,
                maxHeatmapRange: this.maxHeatmapRange
            };
        },
        prepareDeletionSortOrder: function() {
            if (this.sortOrderRecipient) {
                // client handling
                this.handleStopSortOrderShare();
            } else if (this.sortOrderRecipients > 0) {
                // source handling
                EventBus.$emit("sort-order-source-deletion", this.id);
                this.$store.commit("releaseColorUsage", this.sortOrderColor);
            }
        },
        prepareDeletionValueScale: function() {
            if (this.valueScaleRecipient) {
                // client handling
                this.handleStopValueScaleShare();
            } else if (this.valueScaleRecipients > 0) {
                // source handling
                EventBus.$emit("value-scale-source-deletion", this.id);
                this.$store.commit(
                    "releaseValueScaleColorUsage",
                    this.valueScaleColor
                );
            }
        },
        handleWidgetDeletion: function() {
            // needs to be separate to distinguish it from moving
            // emit events for sort-order update
            this.prepareDeletionSortOrder();
            this.prepareDeletionValueScale();
            this.deleteWidget();
        },
        deleteWidget: function() {
            // release color
            if (this.sortOrderRecipients > 0) {
                this.$store.commit("releaseColorUsage", this.sortOrderColor);
            }
            if (this.valueScaleRecipients > 0) {
                this.$store.commit("releaseValueScaleColorUsage", this.valueScaleColor);
            }
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
        initializeForFirstTime: function(widgetData, collectionConfig) {
            var data = {
                widgetDataRef: undefined,
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: collectionConfig["availableData"]["stackup"],
                minHeatmap: undefined,
                maxHeatmap: undefined,
                selectedSortOrder: "center column",
                sortorders: undefined,
                isAscending: true,
                expectingSortOrder: false,
                sortOrderSelectionState: false,
                showSelection: false,
                sortOrderRecipient: false,
                sortOrderRecipients: 0,
                sortOrderTargetID: false,
                sortOrderColor: undefined,
                showMenu: false,
                valueScaleRecipient: false,
                valueScaleRecipients: 0,
                valueScaleSelectionState: false,
                valueScaleTargetID: false,
                valueScaleColor: undefined,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined,
                expectingValueScale: false,
            };
            // write properties to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            return data;
        },
        initializeFromStore: function(widgetData, collectionConfig) {
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
            // increment dataset usage in store
            if (widgetData["dataset"]) {
                let datasetId = widgetData["dataset"];
                this.$store.commit(
                    "compare/increment_usage_dataset",
                    datasetId
                );
            }
            // set color usage in store
            this.$store.commit("setColorUsage", widgetData["sortOrderColor"]);
            this.$store.commit("setValueScaleColorUsage", widgetData["valueScaleColor"])
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedSortOrder: widgetData["selectedSortOrder"],
                minHeatmap: widgetData["minHeatmap"],
                maxHeatmap: widgetData["maxHeatmap"],
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: collectionConfig["availableData"]["stackup"],
                sortorders: widgetData["sortorders"],
                isAscending: widgetData["isAscending"],
                expectingSortOrder: false,
                showSelection: false,
                sortOrderSelectionState: false,
                sortOrderRecipient: widgetData["sortOrderRecipient"],
                sortOrderRecipients: widgetData["sortOrderRecipients"],
                sortOrderTargetID: widgetData["sortOrderTargetID"],
                sortOrderColor: widgetData["sortOrderColor"],
                minHeatmapRange: widgetData["minHeatmapRange"],
                maxHeatmapRange: widgetData["maxHeatmapRange"],
                showMenu: false,
                expectingValueScale: false,
                valueScaleSelectionState: false,
                valueScaleRecipient: widgetData["valueScaleRecipient"],
                valueScaleRecipients: widgetData["valueScaleRecipients"],
                valueScaleTargetID: widgetData["valueScaleTargetID"],
                valueScaleColor: widgetData["valueScaleColor"]
            };
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
        },
        updateData: async function() {
            // reset min and max colormap values
            (this.minHeatmap = undefined), (this.maxHeatmap = undefined);
            // fetch widget data
            var stackup_id = this.binsizes[this.selectedBinsize];
            this.widgetDataRef = stackup_id;
            var data = await this.getStackupData(stackup_id);
            this.widgetData = data;
            // fetch metadata
            var response = await this.fetchData(
                `individualIntervalData/${stackup_id}/metadatasmall`
            );
            // check if shared value is in sortorders and add it if so
            if (this.sortorders && "shared" in this.sortorders) {
                let tempSortOrder = response.data;
                tempSortOrder["shared"] = this.sortorders["shared"];
                this.sortorders = tempSortOrder;
            } else {
                this.sortorders = response.data;
            }
            // add by center column
            this.sortorders["center column"] = {};
            // add random sort order
            seedrandom("I am a random seed!");
            let randArray = [];
            for (let index = 0; index < data.shape[0]; index++) {
                randArray.push(Math.random());
            }
            this.sortorders["random"] = randArray;
            // emit sort order update event
            this.broadcastSortOrderUpdate();
            this.broadcastValueScaleUpdate()
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
                    ]["stackup"];
                this.intervalSize =
                    newValue[this.collectionID]["collectionConfig"][
                        "intervalSize"
                    ];
            }
        },
        datasets: function(newVal, oldVal) {
            if (!newVal || !oldVal || !this.selectedDataset) {
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
            if (!newVal || !oldVal || !this.selectedDataset) {
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
        selectedDataset: function(newVal, oldVal) {
            if (!this.selectedDataset) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // reset min and max colormap values
            (this.minHeatmap = undefined), (this.maxHeatmap = undefined);
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
            // add dataset to store for tallying used_dataset
            this.$store.commit("compare/decrement_usage_dataset", oldVal);
            this.$store.commit("compare/increment_usage_dataset", newVal);
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            this.updateData();
        },
        isAscending: function() {
            // check if selected sort order changes if widget is a sort order donor
            if (this.sortOrderRecipients > 0) {
                this.broadcastSortOrderUpdate();
            }
        },
        selectedSortOrder: function(val) {
            // check if selected sort order changes if widget is a sort order donor
            if (this.sortOrderRecipients > 0) {
                this.broadcastSortOrderUpdate();
            }
        }
    },
    mounted: function() {
        this.registerSortOrderEventHandlers();
        this.registerValueScaleEventHandlers()
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
    margin: 2px;
}

.md-field {
    min-height: 30px;
}
</style>
