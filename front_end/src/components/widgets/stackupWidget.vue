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
import { apiMixin, formattingMixin, widgetMixin } from "../../mixins";
import {
    sort_matrix_by_index,
    sort_matrix_by_center_column,
    get_indices_center_column
} from "../../functions";
import EventBus from "../../eventBus";

const TOOLBARHEIGHT = 71;

export default {
    name: "stackupWidget",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    components: {
        heatmap
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
            if (this.intervalSize) {
                return true;
            }
            return false;
        },
        allowBinsizeSelection: function() {
            return Object.keys(this.binsizes).length != 0;
        },
        cssStyle: function() {
            let opacity = this.showSelection ? "0.6" : "1";
            // define border style
            let borderStyle;
            if (this.sortOrderRecipients > 0) {
                borderStyle = "solid";
            } else if (this.sortOrderTargetID) {
                // sort order target id is defined if widget takes sort order from somewhere else
                borderStyle = "dashed";
            } else {
                borderStyle = "none";
            }
            return {
                height: `${this.height}px`,
                width: `${this.width}px`,
                opacity: opacity,
                "box-sizing": "border-box",
                "border-width": "10px",
                "border-style": `none none ${borderStyle} none`,
                "border-color": this.sortOrderColor
                    ? this.sortOrderColor
                    : "none"
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
        },
        allowSortOrderTargetSelection: function() {
            return (
                this.sortOrderSelectionState &&
                this.showData &&
                !this.sortOrderRecipient
            );
        }
    },
    methods: {
        broadcastSortOrderUpdate: function() {
            // tell client widgets that sort order has changed
            EventBus.$emit(
                "update-sort-order-sharing",
                this.id,
                this.constructSortOrder(),
                this.isAscending
            );
        },
        constructSortOrder: function() {
            // extracts sort order values from current selected sort-order
            let values;
            if (this.selectedSortOrder == "center column") {
                values = get_indices_center_column(
                    this.widgetData["data"],
                    this.widgetData["shape"]
                );
            } else {
                values = this.sortorders[this.selectedSortOrder];
            }
            return values;
        },
        manageColorUpdate: function() {
            // checks which colors are used for sort order sharing and sets a new one
            let returnedColor = this.$store.getters.getNextSortOrderColor;
            if (!returnedColor) {
                return this.colorExhaustionErrorHandler();
            } else {
                this.setBorderColor(returnedColor);
            }
        },
        colorExhaustionErrorHandler: function() {
            // error handler for when there are no more colors to be shared
            alert("Maximum number of shares reached!");
            this.emitEmptySortOrderEnd();
            this.showSelection = false;
            return;
        },
        setBorderColor: function(color) {
            // sets color for widget and commits to store
            this.sortOrderColor = color;
            this.$store.commit("setColorUsage", this.sortOrderColor);
        },
        handleMouseEnter: function() {
            if (this.allowSortOrderTargetSelection) {
                this.showSelection = true;
            }
        },
        handleMouseLeave: function() {
            if (this.allowSortOrderTargetSelection) {
                this.showSelection = false;
            }
        },
        handleWidgetSelection: function() {
            if (this.allowSortOrderTargetSelection) {
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
            }
        },
        handleStartSortOrderShare: function() {
            EventBus.$emit(
                "select-sort-order-start",
                this.id,
                this.collectionID
            );
            // add event listener to window to catch next click event
            window.addEventListener("click", this.emitEmptySortOrderEnd, {
                once: true
            });
            this.expectingSortOrder = true; // this needs to be closed after receiving again -> otherwise everything updates
        },
        handleStopSortOrderShare: function() {
            this.selectedSortOrder = "center column";
            EventBus.$emit("stop-sort-order-sharing", this.sortOrderTargetID);
            this.$delete(this.sortorders, "shared");
            this.sortOrderRecipient = false;
            this.sortOrderTargetID = undefined;
        },
        emitEmptySortOrderEnd: function() {
            EventBus.$emit("select-sort-order-end", undefined, undefined);
        },
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
                isAscending: this.isAscending,
                expectingSortOrder: false,
                sortOrderSelectionState: false,
                showSelection: false,
                sortOrderRecipient: this.sortOrderRecipient,
                sortOrderRecipients: this.sortOrderRecipients,
                sortOrderTargetID: this.sortOrderTargetID,
                sortOrderColor: this.sortOrderColor
            };
        },
        handleWidgetDeletion: function() {
            // needs to be separate to distinguish it from moving
            // emit events for sort-order update
            if (this.sortOrderRecipient) {
                // client handling
                this.handleStopSortOrderShare();
            } else if (this.sortOrderRecipients > 0) {
                // source handling
                EventBus.$emit("sort-order-source-deletion", this.id);
                this.$store.commit("releaseColorUsage", this.sortOrderColor);
            }
            this.deleteWidget();
        },
        deleteWidget: function() {
            // release color
            if (this.sortOrderRecipients > 0) {
                this.$store.commit("releaseColorUsage", this.sortOrderColor);
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
                newCollectionData["regionID"] !=
                    oldCollectionData["regionID"] ||
                newCollectionData["intervalSize"] !=
                    oldCollectionData["intervalSize"]
            ) {
                return false;
            }
            return true;
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
                showMenu: false
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
                showMenu: false
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
            // emit sort order update event
            this.broadcastSortOrderUpdate();
        },
        acceptSortOrderEndEvent: function(
            target_id,
            sortorder,
            direction,
            color
        ) {
            // checks whether passed event arguments are valid and widget is in right state
            return (
                this.expectingSortOrder &&
                target_id &&
                sortorder != undefined &&
                direction &&
                color
            );
        },
        registerSortOrderClientHandlers: function() {
            // register event handlers that are relevant when widget is a sort order share client
            EventBus.$on(
                "select-sort-order-end",
                (target_id, sortorder, direction, color) => {
                    if (
                        this.acceptSortOrderEndEvent(
                            target_id,
                            sortorder,
                            direction,
                            color
                        )
                    ) {
                        // recipient stores data
                        this.$set(this.sortorders, "shared", sortorder);
                        this.selectedSortOrder = "shared";
                        this.isAscending = direction;
                        this.sortOrderTargetID = target_id;
                        this.sortOrderColor = color;
                        this.sortOrderRecipient = true;
                    }
                    this.expectingSortOrder = false; // switches off expecting recipient
                    this.sortOrderSelectionState = false; // switches off donors
                }
            );
            EventBus.$on(
                "update-sort-order-sharing",
                (target_id, sortorder, direction) => {
                    if (
                        this.sortOrderTargetID &&
                        target_id == this.sortOrderTargetID
                    ) {
                        this.$set(this.sortorders, "shared", sortorder);
                        this.selectedSortOrder = "shared";
                        this.isAscending = direction;
                    }
                }
            );
            EventBus.$on("widget-id-change", (old_id, new_id) => {
                if (
                    this.sortOrderRecipient &&
                    old_id == this.sortOrderTargetID
                ) {
                    this.sortOrderTargetID = new_id;
                }
            });
            EventBus.$on("sort-order-source-deletion", source_id => {
                if (this.sortOrderTargetID == source_id) {
                    this.handleStopSortOrderShare();
                }
            });
        },
        registerSortOrderSourceHandlers: function() {
            // handlers that are needed if widget is a sort order source
            EventBus.$on("select-sort-order-start", (id, parent_id) => {
                if (id != this.id && parent_id == this.collectionID) {
                    this.sortOrderSelectionState = true;
                }
            });
            EventBus.$on("stop-sort-order-sharing", target_id => {
                if (target_id == this.id) {
                    this.sortOrderRecipients -= 1;
                    if (this.sortOrderRecipients == 0) {
                        this.$store.commit(
                            "releaseColorUsage",
                            this.sortOrderColor
                        );
                    }
                }
            });
        },
        registerSortOrderEventHandlers: function() {
            // event bus listeners for sort order sharing
            this.registerSortOrderClientHandlers();
            this.registerSortOrderSourceHandlers();
        },
        registerLifeCycleEventHandlers: function() {
            // registers event handlers that react to life cycle event such as deletion and serialization
            EventBus.$on("serialize-widgets", this.serializeWidget);
            // widget deletion can be trigered via event bus from widget collection
            EventBus.$on("delete-widget", id => {
                if (id == this.id) {
                    this.deleteWidget();
                }
            });
        },
        removeEventHandlers: function() {
            EventBus.$off("serialize-widgets", this.serializeWidget);
        },
        getCenterOfArray: function(array) {
            // returns value of center entry in array (rounded down)
            return Number(array[Math.floor(array.length / 2)]);
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
        this.registerLifeCycleEventHandlers();
        this.registerSortOrderEventHandlers();
    },
    beforeDestroy: function() {
        this.removeEventHandlers();
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
