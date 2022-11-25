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
                    class="md-layout-item md-size-45 padding-left padding-right"
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
                                    getBinSizeFormat(binsize)
                                }}</span>
                                <md-icon v-if="selectedBinsize == binsize"
                                    >done</md-icon
                                >
                            </md-menu-item>
                        </md-menu-content>
                    </md-menu>
                </div>
                <div
                    class="md-layout-item md-size-5 toggle-paired-buttons"
                >
                    <div v-if="isBedpeFile" class="no-padding-top md-icon-button">
                        <md-button class="md-icon" :class="{'md-primary': pairedLeftSide}"  @click="togglePairedSides('left')">
                            <md-icon>looks_one</md-icon>
                            <md-tooltip md-direction="top" md-delay="300">
                                Plot left support data
                            </md-tooltip>
                        </md-button>
                    </div>
                </div>
                <div
                    class="md-layout-item md-size-10 toggle-paired-buttons"
                >
                    <div v-if="isBedpeFile" class="no-padding-top">
                        <md-button class="md-icon md-mini" :class="{'md-primary': pairedRightSide}" @click="togglePairedSides('right')" style="margin-left: 8px">
                            <md-icon>looks_two</md-icon>
                        </md-button>
                            <md-tooltip md-direction="top" md-delay="300">
                                Plot right support data
                            </md-tooltip>
                    </div>
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
                            <md-list-item md-expand>
                                <span class="md-body-1">Neighborhood size</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            clusterNumber = 'small';
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Large</span>
                                        <md-icon
                                            v-if="clusterNumber === 'small'"
                                            >done</md-icon
                                        >
                                    </md-list-item>
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            clusterNumber = 'large';
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Small</span>
                                        <md-icon
                                            v-if="clusterNumber === 'large'"
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
            <div style="position: relative">
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
                    @heatmap-clicked="handleHeatmapClick"
                    @mouse-move="handleMouseMove"
                    @mouse-enter="handleMouseEnter"
                    @mouse-leave="handleMouseLeftTooltip"
                    @mouse-leave-container="handleMouseLeftContainer"
                    :log="false"
                />
                <tooltip
                    :id="id"
                    :width="width"
                    :height="tooltipHeight"
                    :showTooltip="showTooltip"
                    :averageValues="averageValues"
                    :showControls="showTooltipControls"
                    :tooltipOffsetLeft="tooltipOffsetLeft"
                    :tooltipOffsetTop="tooltipOffsetTop"
                    :clusterID="selectedCluster"
                    :embeddingID="widgetDataID"
                    :collectionName="collectionName"
                    :regionName="regionName"
                    :datasetNames="datasetNames"
                    @close-controls="closeControls"
                    :clusterCounts="clusterCounts"
                />
            </div>
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
import tooltip from "../visualizations/barPlotTooltip.vue";

export default {
    components: { heatmap, tooltip },
    name: "Embedding1D",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    computed: {
        waitSpinnerContainer: function() {
            return {
                height: this.visualizationHeight + "px",
                width: this.width + "px",
                display: "flex",
                "justify-content": "center",
                "align-items": "center"
            };
        },
        colormap: function() {
            if (this.overlay == "density") {
                return "viridis";
            }
            return "magma";
        },
        tooltipHeight: function() {
            if (this.showTooltipControls) {
                return this.height + 10;
            }
            return this.height - 30;
        },
        collectionName: function() {
            if (this.selectedBinsize) {
                return this.datasets[this.selectedDataset]["name"];
            }
        },
        message: function() {
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
                this.getBinSizeFormat(this.selectedBinsize)
            );
        },
        size: function() {
            if (!this.widgetData) {
                return;
            }
            if (this.widgetData["embedding"]["shape"][0] > 50000) {
                return 150;
            }
            if (this.widgetData["embedding"]["shape"][0] > 10000) {
                return 100;
            }
            if (this.widgetData["embedding"]["shape"][0] > 2500) {
                return 50;
            }
            return 25;
        },
        clusterMap: function() {
            return rectBin(
                this.size,
                this.widgetData["embedding"].data,
                this.widgetData["cluster_ids"].data,
                "mode"
            );
        },
        aggregationType: function() {
            if (this.overlay == "density") {
                return "sum";
            }
            return "mean";
        },
        averageValues: function() {
            if (!this.widgetData) {
                return;
            }
            return this.widgetData["thumbnails"];
        },
        clusterCounts: function() {
            if (!this.widgetData) {
                return;
            }
            // count how many of which cluster are there
            let clusterCounts = new Map();
            for (let cluster_id of this.widgetData["cluster_ids"]["data"]) {
                if (clusterCounts.has(cluster_id)) {
                    clusterCounts.set(
                        cluster_id,
                        clusterCounts.get(cluster_id) + 1
                    );
                } else {
                    clusterCounts.set(cluster_id, 1);
                }
            }
            return clusterCounts;
        },
        embeddingData: function() {
            if (!this.widgetData) {
                return;
            }
            if (this.selectedCluster === undefined) {
                return {
                    data: flatten(
                        rectBin(
                            this.size,
                            this.widgetData["embedding"]["data"],
                            this.overlayValues,
                            this.aggregationType
                        )
                    ),
                    shape: [this.size, this.size],
                    dtype: "float32"
                };
            }
            let overlayClusters = this.widgetData["cluster_ids"]["data"].map(
                el => {
                    if (el === this.selectedCluster) {
                        return 99999999;
                    }
                    return 1;
                }
            );
            return {
                data: flatten(
                    rectBin(
                        this.size,
                        this.widgetData["embedding"].data,
                        overlayClusters,
                        "mean"
                    )
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
        },
        widgetDataID: function() {
            if (this.binsizes && this.selectedBinsize) {
                return Number(
                    this.binsizes[this.selectedBinsize][this.clusterNumber]
                );
            }
        }
    },
    methods: {
        startDatasetSelection: function() {
            this.expectSelection = true;
            // get collections from store
            let collections = this.$store.state.collections.filter(el =>
                Object.keys(this.datasets).includes(String(el.id))
            );
            let preselection = this.selectedDataset
                ? [this.selectedDataset]
                : [];
            EventBus.$emit(
                "show-select-collection-dialog",
                collections,
                "1d-features",
                preselection
            );
        },
        registerSelectionEventHandlers: function() {
            EventBus.$on("collection-selected", this.handleDataSelection);
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion);
        },
        removeSelectionEventHandlers: function() {
            EventBus.$off("collection-selected", this.handleDataSelection);
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion);
        },
        handleDataSelection: function(id) {
            if (this.expectSelection) {
                this.selectedDataset = id;
                this.expectSelection = false;
            }
        },
        hanldeSelectionAbortion: function() {
            this.expectSelection = false;
        },
        handleHeatmapClick: function(x, y, adjustedX, adjustedY) {
            if (this.showTooltipControls) {
                this.showTooltipControls = false;
            } else if (this.showTooltip && this.selectedCluster !== undefined) {
                this.showTooltipControls = true;
            }
        },
        handleMouseMove: function(x, y, adjustedX, adjustedY, size) {
            if (!this.showTooltipControls) {
                this.showTooltip = true;
                this.tooltipOffsetLeft = adjustedX + 60;
                this.tooltipOffsetTop = adjustedY;
                this.selectCluster(x, y, size);
            }
        },
        handleMouseEnter: function(x, y, adjustedX, adjustedY) {
            if (!this.showTooltipControls) {
                this.showTooltip = true;
                this.tooltipOffsetLeft = adjustedX + 60;
                this.tooltipOffsetTop = adjustedY;
            }
        },
        handleMouseLeftTooltip: function() {
            if (!this.showTooltipControls) {
                this.showTooltip = false;
            }
        },
        handleMouseLeftContainer: function() {
            if (!this.showTooltipControls) {
                this.selectedCluster = undefined;
            }
        },
        areBinsOutsideClusterMapBounds(x_bin, y_bin) {
            // checks whether x_bin, y_bin is within clustermap bounds
            if (x_bin < 0 || y_bin < 0) {
                return true;
            }
            if (x_bin > this.size - 1 || y_bin > this.size - 1) {
                return true;
            }
            return false;
        },
        selectCluster: function(x, y, visualizationSize) {
            let bin_width = visualizationSize / this.size;
            let x_bin = Math.round(x / bin_width);
            let y_bin = Math.round(y / bin_width);
            if (this.clusterMap) {
                // guard against weird artefacts
                if (this.areBinsOutsideClusterMapBounds(x_bin, y_bin)) {
                    this.selectedCluster = undefined;
                    return;
                }
                this.selectedCluster = this.clusterMap[y_bin][x_bin];
            }
        },
        closeControls: function() {
            this.selectedCluster = undefined;
            this.showTooltipControls = false;
            this.showTooltip = false;
        },
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
                maxHeatmapRange: this.maxHeatmapRange,
                clusterNumber: this.clusterNumber,
                selectedCluster: this.selectedCluster,
                pairedLeftSide: this.pairedLeftSide,
                pairedRightSide: this.pairedRightSide,
                pairedSidesMutuallyExclusive: this.pairedSidesMutuallyExclusive,
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
                regionName: collectionData["regionName"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: {},
                datasets:
                    collectionData["datasetsForIntervalSize"]["embedding1d"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                overlay: "density",
                clusterNumber: "small",
                minHeatmap: undefined,
                maxHeatmap: undefined,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined,
                overlayValues: undefined,
                loading: false,
                selectedCluster: undefined,
                showTooltip: false,
                showTooltipControls: false,
                tooltipOffsetTop: 0,
                tooltipOffsetLeft: 0,
                pairedLeftSide: true,
                pairedRightSide: false,
                pairedSidesMutuallyExclusive: true,
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
            var overlayValues;
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
                // get overlay data from store
                var payloadOverlay = {
                    id: widgetData["widgetDataRef"],
                    overlayIndex: Number(widgetData["overlay"])
                };
                // get overlay data from store
                var overlayValues = this.$store.getters[
                    "compare/getWidgetDataEmbedding1d"
                ](payloadOverlay);
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
                regionName: collectionConfig["regionName"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets:
                    collectionConfig["datasetsForIntervalSize"]["embedding1d"],
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
                clusterNumber: widgetData["clusterNumber"],
                selectedCluster: widgetData["selectedCluster"],
                showTooltipControls: false,
                showTooltip: false,
                tooltipOffsetTop: 0,
                tooltipOffsetLeft: 0,
                pairedLeftSide: widgetData["pairedLeftSide"] !== undefined ? widgetData["pairedLeftSide"] : true,
                pairedRightSide: widgetData["pairedRightSide"] !== undefined ? widgetData["pairedRightSide"] : false,
                pairedSidesMutuallyExclusive: true,
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
        getOverlayData: async function(id, index) {
            var queryObject = {
                id: id,
                overlayIndex: index
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
            let data;
            let response;
            if (requestData) {
                response = await requestData;
                data = response.data;
                if (this.isBedpeFile) {
                    if (this.pairedLeftSide) {
                        data = response.data[0];
                    } else {
                        data = response.data[1];
                    }
                }
            } else {
                // request has not been dispatched => put it in store
                this.$store.commit("compare/setRequest", {
                    url: url,
                    data: this.fetchData(url)
                });
                response = await this.$store.getters["compare/getRequest"](url);
                data = response.data;
                if (this.isBedpeFile) {
                    if (this.pairedLeftSide) {
                        data = response.data[0];
                    } else {
                        data = response.data[1];
                    }
                }
                // save it in store -> only first request needs to persist it
                var mutationObject = {
                    id: id,
                    overlayIndex: index,
                    data: data["data"]
                };
                this.$store.commit(
                    "compare/setWidgetDataEmbedding1d",
                    mutationObject
                );
            }
            return data["data"];
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
            // pileup does not exists in store, check whether request has been dispatched
            let url = `embeddingIntervalData/${id}/`;
            let requestData = this.$store.getters["compare/getRequest"](url);
            let data;
            let response;
            if (requestData) {
                response = await requestData;
                if (this.isBedpeFile) {
                    if (this.pairedLeftSide) {
                        data = data[0];
                    } else {
                        data = data[1];
                    }
                }
            } else {
                // request has not been dispatched => put it in store
                this.$store.commit("compare/setRequest", {
                    url: url,
                    data: this.fetchData(url)
                });
                response = await this.$store.getters["compare/getRequest"](url);
                data = response.data;
                if (this.isBedpeFile) {
                    if (this.pairedLeftSide) {
                        data = data[0];
                    } else {
                        data = data[1];
                    }
                }
                // save it in store -> only first request needs to persist it
                var mutationObject = {
                    id: id,
                    data: response.data
                };
                this.$store.commit(
                    "compare/setWidgetDataEmbedding1d",
                    mutationObject
                );
            }
            // return it
            return data;
        },
        updateData: async function() {
            this.loading = true;
            // construct data ids to be fecthed
            let selected_id = this.binsizes[this.selectedBinsize][
                this.clusterNumber
            ];
            // store widget data ref
            this.widgetDataRef = selected_id;
            // fetch data
            var data = await this.getEmbeddingData(selected_id);
            this.widgetData = data;
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
            this.loading = false;
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
                        "datasetsForIntervalSize"
                    ]["embedding1d"];
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
            // check whether binsizes are defined
            if (this.binsizes === undefined) {
                // not data exists, blank widget DAta
                this.widgetData = undefined;
                return;
            }
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
            // check whether binsizes are defined
            if (this.binsizes === undefined) {
                // not data exists, blank widget DAta
                this.widgetData = undefined;
                return;
            }
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
            // check whether binsizes are defined
            if (this.binsizes === undefined) {
                // not data exists, blank widget DAta
                this.widgetData = undefined;
                return;
            }
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
        },
        overlay: async function() {
            // fetch overlay if needed
            this.loading = true;
            if (this.overlay != "density") {
                let selected_id = this.binsizes[this.selectedBinsize][
                    this.clusterNumber
                ];
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
        clusterNumber: function() {
            if (!this.selectedBinszie) {
                this.updateData();
            }
        }
    },
    mounted: function() {
        this.registerSelectionEventHandlers();
    },
    beforeDestroy: function() {
        this.removeSelectionEventHandlers();
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

.toggle-paired-buttons {
    padding-top: 8px;
    padding-bottom:8px;
}
</style>
