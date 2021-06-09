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
                                            <md-switch v-model="isAscending" :disabled="sortOrderRecipient"
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
                                        @click="handleStartSortOrderShare" :disabled="sortOrderRecipient || this.sortOrderRecipients > 0"
                                        ><span class="md-body-1"
                                            >Take sort order from</span
                                        >
                                    </md-list-item>
                                    <md-list-item @click="handleStopSortOrderShare" :disabled="!sortOrderRecipient">
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
import { apiMixin, formattingMixin } from "../../mixins";
import {
    sort_matrix_by_index,
    sort_matrix_by_center_column,
    get_indices_center_column
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
            if (this.sortOrderRecipients > 0){
                borderStyle = "solid"
            }else if (this.sortOrderTargetID){ // sort order target id is defined if widget takes sort order from somewhere else
                borderStyle = "dashed"
            }else{
                borderStyle = "none"
            }
            return {
                height: `${this.height}px`,
                width: `${this.width}px`,
                opacity: opacity,
                "box-sizing": "border-box",
                "border-width": "10px",
                "border-style": `none none ${borderStyle} none`,
                "border-color": this.sortOrderColor ? this.sortOrderColor: "none"
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
        handleMouseEnter: function() {
            if (this.sortOrderSelectionState && this.showData && !this.sortOrderRecipient) {
                this.showSelection = true;
            }
        },
        handleMouseLeave: function() {
            if (this.sortOrderSelectionState && this.showData && !this.sortOrderRecipient) {
                this.showSelection = false;
            }
        },
        handleWidgetSelection: function() {
            if (this.sortOrderSelectionState && this.showData && !this.sortOrderRecipient) {
                // construct sort order -> the values are just shared and sorting is done in target widget
                let values;
                if (this.selectedSortOrder == "center column"){
                    values = get_indices_center_column(this.widgetData["data"], this.widgetData["shape"])
                }else{
                    values = this.sortorders[this.selectedSortOrder]
                }
                if (this.sortOrderRecipients == 0){
                    // new share established, get current color
                    this.sortOrderColor = this.$globalFlags.sortOrderShareColors[this.$globalFlags.sortOrderColorIndex]
                    // increment index
                    this.$globalFlags.sortOrderColorIndex += 1
                }
                EventBus.$emit(
                    "select-sort-order-end",
                    this.id,
                    values,
                    this.isAscending,
                    this.sortOrderColor
                );
                this.sortOrderRecipients += 1;
                this.showSelection = false;
            }
        },
        handleStartSortOrderShare: function() {
            EventBus.$emit("select-sort-order-start", this.id);
            // add event listener to window to catch next click event
            window.addEventListener(
                "click", this.emitEmptySortOrderEnd,
                { once: true }
            );
            this.expectingSortOrder = true // this needs to be closed after receiving again -> otherwise everything updates
        },
        handleStopSortOrderShare: function(){
            this.selectedSortOrder = "center column"
            EventBus.$emit("stop-sort-order-sharing", this.sortOrderTargetID)
            this.$delete(this.sortorders, "shared")
            this.sortOrderRecipient = false;
            this.sortOrderTargetID = undefined;
        },
        emitEmptySortOrderEnd: function(){
            EventBus.$emit(
                        "select-sort-order-end",
                        undefined,
                        undefined
                    );
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
        handleWidgetDeletion: function(){
            // needs to be separate to distinguish it from moving
            // emit events for sort-order update
            if (this.sortOrderRecipient){
                // client handling
                this.handleStopSortOrderShare()
            }else if (this.sortOrderRecipients > 0){
                // source handling
                EventBus.$emit("sort-order-source-deletion", this.id)
            }
            this.deleteWidget()
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
                newCollectionData["regionID"] !=
                    oldCollectionData["regionID"] ||
                newCollectionData["intervalSize"] !=
                    oldCollectionData["intervalSize"]
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
                intervalSize: collectionData["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: collectionData["availableData"]["stackup"],
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
        initializeAtNewCollection: function(widgetData, collectionConfig) {
            return {
                widgetDataRef: undefined,
                minHeatmap: undefined,
                maxHeatmap: undefined,
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                selectedSortOrder: "center column",
                datasets: collectionData["availableData"]["stackup"],
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
        },
        initializeAtSameCollection: function(widgetData, collectionConfig) {// TODO: watcher for select-start-order start does not work when client is moved
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
            this.sortorders = response.data;
            // add by center column
            this.sortorders["center column"] = {};
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
            let binsizes = Object.keys(this.binsizes);
            this.selectedBinsize = Number(
                binsizes[Math.floor(binsizes.length / 2)]
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
            let binsizes = Object.keys(this.binsizes);
            this.selectedBinsize = Number(
                binsizes[Math.floor(binsizes.length / 2)]
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
            let binsizes = Object.keys(this.binsizes);
            if (!this.selectedBinsize) {
                this.selectedBinsize = Number(
                    binsizes[Math.floor(binsizes.length / 2)]
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
            if (this.sortOrderRecipients > 0){
                let values;
                if (this.selectedSortOrder == "center column"){
                    values = get_indices_center_column(this.widgetData["data"], this.widgetData["shape"])
                }else{
                    values = this.sortorders[this.selectedSortOrder]
                }
                EventBus.$emit("update-sort-order-sharing", this.id, values, this.isAscending)
            }
        },
        selectedSortOrder: function(val){
            // check if selected sort order changes if widget is a sort order donor
            if (this.sortOrderRecipients > 0){
                let values;
                if (this.selectedSortOrder == "center column"){
                    values = get_indices_center_column(this.widgetData["data"], this.widgetData["shape"])
                }else{
                    values = this.sortorders[this.selectedSortOrder]
                }
                EventBus.$emit("update-sort-order-sharing", this.id, values, this.isAscending)
            }
        }
    },
    mounted: function() {
        EventBus.$on("serialize-widgets", this.serializeWidget);
        // widget deletion can be trigered via event bus from widget collection
        EventBus.$on("delete-widget", id => {
            if (id == this.id) {
                this.deleteWidget();
            }
        });
        // event bus listeners for sort order sharing
        EventBus.$on("select-sort-order-start", id => {
            if (id != this.id) {
                this.sortOrderSelectionState = true;
            }
        });
        EventBus.$on("select-sort-order-end", (target_id, sortorder, direction, color) => {
            if (this.expectingSortOrder && target_id && sortorder && direction && color){
                // recipient stores data
                this.$set(this.sortorders, "shared", sortorder);
                this.selectedSortOrder = "shared"
                this.isAscending = direction
                this.sortOrderTargetID = target_id
                this.sortOrderColor = color
                this.sortOrderRecipient = true
            }
            this.expectingSortOrder = false; // switches off expecting recipient
            this.sortOrderSelectionState = false; // switches off donors
        });
        EventBus.$on("stop-sort-order-sharing", (target_id) => {
            if (target_id == this.id){
                this.sortOrderRecipients -= 1
                if (this.sortOrderRecipients == 0){
                    this.$globalFlags.sortOrderColorIndex -= 1
                }
            }
        });
        EventBus.$on("update-sort-order-sharing", (target_id, sortorder, direction) => {
            if (this.sortOrderTargetID && (target_id == this.sortOrderTargetID)){
                this.$set(this.sortorders, "shared", sortorder);
                this.selectedSortOrder = "shared"
                this.isAscending = direction
            }
        })
        EventBus.$on("widget-id-change", (old_id, new_id) => {
            if (this.sortOrderRecipient && old_id == this.sortOrderTargetID){
                this.sortOrderTargetID = new_id
            }
        })
        EventBus.$on("sort-order-source-deletion", (source_id) => {
            if (this.sortOrderTargetID == source_id){
                this.handleStopSortOrderShare()
            }
        })
    },
    beforeDestroy: function() {
        EventBus.$off("serialize-widgets");
        // delete widget does not need to be taken off the event bus as ids don't get reused
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
