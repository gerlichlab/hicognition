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
                    <div class="menu-button">
                        <md-button
                            class="md-icon-button"
                            @click="startDatasetSelection"
                            :disabled="!allowDatasetSelection"
                        >
                            <md-icon>menu_open</md-icon>
                            <md-tooltip md-direction="top" md-delay="300"
                                >Select a dataset for this widget</md-tooltip
                            >
                        </md-button>
                    </div>
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
                v-if="showData && !loading"
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
            <div v-if="loading" :style="waitSpinnerContainer">
                <md-progress-spinner
                    :md-diameter="100"
                    :md-stroke="10"
                    md-mode="indeterminate"
                ></md-progress-spinner>
            </div>
            <div
                v-if="!showData && !loading"
                class="md-layout md-alignment-center-center"
                style="height: 89%"
            >
                <md-icon class="md-layout-item md-size-50 md-size-5x"
                    >input</md-icon
                >
            </div>
            <div class="flex-container" v-if="showData || loading">
                <div>
                    <span class="md-caption">{{ message }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { apiMixin, formattingMixin, widgetMixin } from "../../mixins";
import { rectBin, flatten } from "../../functions";
import heatmap from "../visualizations/heatmap.vue";
import EventBus from "../../eventBus";

export default {
    components: { heatmap },
    name: "Embedding1D",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    computed: {
        waitSpinnerContainer: function () {
            return {
                height: this.visualizationHeight + "px",
                width: this.width+ "px",
                display: "flex",
                "justify-content": "center",
                "align-items": "center"
            };
        },
        colormap: function () {
            if (this.overlay == "density"){
                return "viridis";
            }
            return "magma"
        },
        message: function () {
            let overlayMessage;
            if (this.overlay == "density") {
                overlayMessage = "point density";
            } else {
                overlayMessage = this.datasetNames[Number(this.overlay)].name;
            }
            return (
                this.datasets[this.selectedDataset]["name"] +
                " | " +
                `${overlayMessage}` +
                " | binsize " +
                this.convertBasePairsToReadable(this.selectedBinsize)
            );
        },
        size: function () {
            if (!this.widgetData) {
                return;
            }
            if (this.widgetData["shape"][0] > 50000){
                return 150
            }
            if (this.widgetData["shape"][0] > 10000) {
                return 100;
            }
            return 50;
        },
        aggregationType: function () {
            if (this.overlay == "density") {
                return "sum";
            }
            return "mean";
        },
        embeddingData: function () {
            return {
                data: flatten(
                    rectBin(
                        this.size,
                        this.widgetData["data"],
                        this.overlayValues,
                        this.aggregationType
                    )
                ),
                shape: [this.size, this.size],
                dtype: "float32",
            };
        },
        datasetNames: function () {
            if (this.selectedDataset.length == 0) {
                return [];
            }
            return this.datasets[this.selectedDataset][
                "collection_dataset_names"
            ].map((el, i) => {
                return {
                    name: el,
                    index: String(i),
                };
            });
        },
    },
    methods: {
        startDatasetSelection: function () {
            this.expectSelection = true;
            // get collections from store
            let collections = this.$store.state.collections.filter( (el) => Object.keys(this.datasets).includes(String(el.id)) )
            let preselection = this.selectedDataset ? [this.selectedDataset] : []
            EventBus.$emit("show-select-collection-dialog", collections, "1d-features" , preselection);
        },
        registerSelectionEventHandlers: function(){
            EventBus.$on("collection-selected", this.handleDataSelection)
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion)
        },
        removeSelectionEventHandlers: function(){
            EventBus.$off("collection-selected", this.handleDataSelection)
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion)
        },
        handleDataSelection: function(id){
            if (this.expectSelection){
                    this.selectedDataset = id
                    this.expectSelection = false
            }
        },
        hanldeSelectionAbortion: function(){
            this.expectSelection = false
        },
        blankWidget: function () {
            // removes all information that the user can set in case a certain region/dataset combination is not available
            this.widgetData = undefined;
            this.selectedDataset = [];
            this.selectedBinsize = undefined;
            this.widgetDataRef = undefined;
        },
        handleDatasetSelection: function (id) {
            this.selectedDataset = id;
        },
        handleBinsizeSelection: function (binsize) {
            this.selectedBinsize = binsize;
        },
        toStoreObject: function () {
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
                maxHeatmapRange: this.maxHeatmapRange,
            };
        },
        initializeForFirstTime: function (widgetData, collectionData) {
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
                minHeatmap: undefined,
                maxHeatmap: undefined,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined,
                overlayValues: undefined,
                loading: false,
            };
            // write properties to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            return data;
        },
        deleteWidget: function () {
            /*
                Needs to be overriden because decrement mutation is different from mixin
            */
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id,
            };
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
            // decrement dataset from used dataset in store
            this.$store.commit(
                "compare/decrement_usage_collections",
                this.selectedDataset
            );
        },
        initializeFromStore: function (widgetData, collectionConfig) {
            var widgetDataValues;
            var overlayValues;
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                // deinfe store queries
                var payload = {
                    id: widgetData["widgetDataRef"],
                };
                // get widget data from store
                var widgetDataValues =
                    this.$store.getters["compare/getWidgetDataEmbedding1d"](
                        payload
                    );
                // get overlay data from store
                var payloadOverlay = {
                    id: widgetData["widgetDataRef"],
                    overlayIndex: Number(widgetData["overlay"]),
                };
                // get overlay data from store
                var overlayValues =
                    this.$store.getters["compare/getWidgetDataEmbedding1d"](
                        payloadOverlay
                    );
            } else {
                widgetDataValues = undefined;
                overlayValues = undefined;
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
                overlayValues: overlayValues,
                minHeatmap: widgetData["minHeatmap"],
                maxHeatmap: widgetData["maxHeatmap"],
                minHeatmapRange: widgetData["minHeatmapRange"],
                maxHeatmapRange: widgetData["maxHeatmapRange"],
                loading: false,
            };
        },
        handleSliderChange: function (data) {
            this.setColorScale(data);
        },
        setColorScale: function (data) {
            /* 
                sets colorScale based on data array
                containing minPos, maxPos, minRange, maxRange
            */
            this.minHeatmap = data[0];
            this.maxHeatmap = data[1];
            this.minHeatmapRange = data[2];
            this.maxHeatmapRange = data[3];
        },
        resetColorScale: function () {
            /*
                resets colorscale to undefined
            */
            this.minHeatmap = undefined;
            this.maxHeatmap = undefined;
            this.minHeatmapRange = undefined;
            this.maxHeatmapRange = undefined;
        },
        getOverlayData: async function (id, index) {
            var queryObject = {
                id: id,
                overlayIndex: index,
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
            // overlay data does not exist, check whether request has been dispatched
            let url = `embeddingIntervalData/${id}/${index}/`;
            let requestData = this.$store.getters["compare/getRequest"](url);
            let response;
            if (requestData) {
                response = await requestData;
            } else {
                // request has not been dispatched => put it in store
                this.$store.commit("compare/setRequest", {
                    url: url,
                    data: this.fetchData(url),
                });
                response = await this.$store.getters["compare/getRequest"](url);
                // save it in store -> only first request needs to persist it
                var mutationObject = {
                    id: id,
                    overlayIndex: index,
                    data: response.data["data"],
                };
                this.$store.commit(
                    "compare/setWidgetDataEmbedding1d",
                    mutationObject
                );
            }
            return response.data["data"];
        },
        getEmbeddingData: async function (id) {
            // checks whether association data is in store and fetches it if it is not
            var queryObject = {
                id: id,
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
            // pileup does not exists in store, check whether request has been dispatched
            let url = `embeddingIntervalData/${id}/`;
            let requestData = this.$store.getters["compare/getRequest"](url);
            let response;
            if (requestData) {
                response = await requestData;
            } else {
                // request has not been dispatched => put it in store
                this.$store.commit("compare/setRequest", {
                    url: url,
                    data: this.fetchData(url),
                });
                response = await this.$store.getters["compare/getRequest"](url);
                // save it in store -> only first request needs to persist it
                var mutationObject = {
                    id: id,
                    data: response.data,
                };
                this.$store.commit(
                    "compare/setWidgetDataEmbedding1d",
                    mutationObject
                );
            }
            // return it
            return response.data;
        },
        updateData: async function () {
            this.loading = true;
            // construct data ids to be fecthed
            let selected_id = this.binsizes[this.selectedBinsize];
            // store widget data ref
            this.widgetDataRef = selected_id;
            // fetch data
            this.widgetData = await this.getEmbeddingData(selected_id);
            // fetch overlay if needed
            if (this.overlay != "density") {
                this.overlayValues = await this.getOverlayData(
                    selected_id,
                    Number(this.overlay)
                );
            } else {
                this.overlayValues = undefined;
            }
            // reset color scale
            this.resetColorScale();
            this.loading = false
        },
    },
    watch: {
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function (newValue) {
                // update availability object
                this.datasets =
                    newValue[this.collectionID]["collectionConfig"][
                        "availableData"
                    ]["embedding"];
                this.intervalSize =
                    newValue[this.collectionID]["collectionConfig"][
                        "intervalSize"
                    ];
            },
        },
        datasets: function (newVal, oldVal) {
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
            this.binsizes =
                this.datasets[this.selectedDataset]["data_ids"][
                    this.intervalSize
                ];
            this.selectedBinsize = this.getCenterOfArray(
                Object.keys(this.binsizes)
            );
            this.updateData();
        },
        intervalSize: function (newVal, oldVal) {
            // if interval size changes, reload data
            if (!newVal || !oldVal || this.selectedDataset.length == 0) {
                return;
            }
            this.binsizes =
                this.datasets[this.selectedDataset]["data_ids"][
                    this.intervalSize
                ];
            this.selectedBinsize = this.getCenterOfArray(
                Object.keys(this.binsizes)
            );
            this.updateData();
        },
        selectedDataset: async function (newVal, oldVal) {
            if (!this.selectedDataset || this.selectedDataset.length == 0) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // set binsizes and add default
            this.binsizes =
                this.datasets[this.selectedDataset]["data_ids"][
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
        selectedBinsize: async function () {
            if (!this.selectedBinsize) {
                return;
            }
            this.updateData();
        },
        overlay: async function () {
            // fetch overlay if needed
            this.loading = true;
            if (this.overlay != "density") {
                let selected_id = this.binsizes[this.selectedBinsize];
                this.overlayValues = await this.getOverlayData(
                    selected_id,
                    Number(this.overlay)
                );
            } else {
                this.overlayValues = undefined;
            }
            this.resetColorScale();
            this.loading = false;
        },
    },
    mounted: function(){
        this.registerSelectionEventHandlers()
    },
    beforeDestroy: function(){
        this.removeSelectionEventHandlers()
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
