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
                                    getBinSizeFormat(binsize)
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
                                <span class="md-body-1">Share</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            shareValueScale = !shareValueScale;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1"
                                            >ValueScale</span
                                        >
                                        <md-icon v-if="shareValueScale"
                                            >done</md-icon
                                        >
                                    </md-list-item>
                                </md-list>
                            </md-list-item>
                            <md-list-item md-expand>
                                <span class="md-body-1">Scale</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            isICCF = true;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">ICCF</span>
                                        <md-icon v-if="isICCF">done</md-icon>
                                    </md-list-item>
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            isICCF = false;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Obs/Exp</span>
                                        <md-icon v-if="!isICCF">done</md-icon>
                                    </md-list-item>
                                </md-list>
                            </md-list-item>
                            <md-list-item md-expand>
                                <span class="md-body-1">Transform</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            isLog = true;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Log</span>
                                        <md-icon v-if="isLog">done</md-icon>
                                    </md-list-item>
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            isLog = false;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Linear</span>
                                        <md-icon v-if="!isLog">done</md-icon>
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
                    :colormap="thumbnailColormap"
                    :allowValueScaleChange="false"
                    :showTooltip="showTooltip"
                    :thumbnail="thumbnail"
                    :distributionData="distributionData"
                    :showControls="showTooltipControls"
                    :tooltipOffsetLeft="tooltipOffsetLeft"
                    :minHeatmapAll="minValueRobust"
                    :maxHeatmapAll="maxValueRobust"
                    :minHeatmapAllRange="minValue"
                    :maxHeatmapAllRange="maxValue"
                    :tooltipOffsetTop="tooltipOffsetTop"
                    :clusterID="selectedCluster"
                    :embeddingID="widgetDataID"
                    :datasetName="datasetName"
                    :regionName="regionName"
                    @close-controls="closeControls"
                    :isLog="isLog"
                    :isVariableSize="isVariableSize"
                    :clusterCounts="clusterCounts"
                    :intervalSize="intervalSize"
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
import {
    rectBin,
    flatten,
    select_3d_along_first_axis,
    getPercentile,
    getPerMilRank,
} from "../../functions";
import heatmap from "../visualizations/heatmap.vue";
import tooltip from "../visualizations/heatmapTooltip.vue";
import EventBus from "../../eventBus";

export default {
    components: { heatmap, tooltip },
    name: "Embedding2D",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    computed: {
        waitSpinnerContainer: function () {
            return {
                height: this.visualizationHeight + "px",
                width: this.width + "px",
                display: "flex",
                "justify-content": "center",
                "align-items": "center",
            };
        },
        thumbnailColormap: function () {
            if (this.valueType == "ICCF") {
                return "fall";
            }
            return "blueWhiteRed";
        },
        tooltipHeight: function () {
            if (this.showTooltipControls) {
                return this.height + 30;
            }
            return this.height - 10;
        },
        colormap: function () {
            return "viridis";
        },
        valueType: function () {
            if (this.isICCF) {
                return "ICCF";
            } else {
                return "ObsExp";
            }
        },
        showData: function () {
            if (this.widgetData && this.widgetData[this.valueType]) {
                return true;
            }
            return false;
        },
        widgetDataID: function () {
            if (this.binsizes && this.selectedBinsize) {
                let valueType;
                if (this.isICCF) {
                    valueType = "ICCF";
                } else {
                    valueType = "Obs/Exp";
                }
                return Number(
                    this.binsizes[this.selectedBinsize][valueType][
                        this.clusterNumber
                    ]
                );
            }
        },
        datasetName: function () {
            if (this.selectedBinsize) {
                return this.datasets[this.selectedDataset]["name"];
            }
        },
        distributionData: function () {
            if (this.widgetData && this.widgetData[this.valueType]) {
                return this.widgetData[this.valueType]["distributions"];
            }
        },
        message: function () {
            let overlayMessage = "point density";
            return (
                this.datasets[this.selectedDataset]["name"] +
                " | " +
                `${overlayMessage}` +
                " | binsize " +
                this.getBinSizeFormat(this.selectedBinsize)
            );
        },
        size: function () {
            if (!this.widgetData || !this.widgetData[this.valueType]) {
                return;
            }
            if (
                this.widgetData[this.valueType]["embedding"]["shape"][0] > 50000
            ) {
                return 150;
            }
            if (
                this.widgetData[this.valueType]["embedding"]["shape"][0] > 10000
            ) {
                return 100;
            }
            if (
                this.widgetData[this.valueType]["embedding"]["shape"][0] > 2500
            ) {
                return 50;
            }
            return 25;
        },
        aggregationType: function () {
            return "sum";
        },
        clusterMap: function () {
            return rectBin(
                this.size,
                this.widgetData[this.valueType]["embedding"].data,
                this.widgetData[this.valueType]["cluster_ids"].data,
                "mode"
            );
        },
        minValueRobust: function () {
            if (!this.shareValueScale || !this.widgetData[this.valueType]) {
                return undefined;
            }
            if (this.isLog) {
                return Math.log2(
                    getPercentile(
                        this.widgetData[this.valueType]["thumbnails"].data,
                        1
                    )
                );
            }
            return getPercentile(
                this.widgetData[this.valueType]["thumbnails"].data,
                1
            );
        },
        maxValueRobust: function () {
            if (!this.shareValueScale || !this.widgetData[this.valueType]) {
                return undefined;
            }
            if (this.isLog) {
                return Math.log2(
                    getPercentile(
                        this.widgetData[this.valueType]["thumbnails"].data,
                        99
                    )
                );
            }
            return getPercentile(
                this.widgetData[this.valueType]["thumbnails"].data,
                99
            );
        },
        minValue: function () {
            if (!this.shareValueScale || !this.widgetData[this.valueType]) {
                return undefined;
            }
            if (this.isLog) {
                return Math.log2(
                    getPerMilRank(
                        this.widgetData[this.valueType]["thumbnails"].data,
                        1
                    )
                );
            }
            return getPerMilRank(
                this.widgetData[this.valueType]["thumbnails"].data,
                1
            );
        },
        maxValue: function () {
            if (!this.shareValueScale || !this.widgetData[this.valueType]) {
                return undefined;
            }
            if (this.isLog) {
                return Math.log2(
                    getPerMilRank(
                        this.widgetData[this.valueType]["thumbnails"].data,
                        999
                    )
                );
            }
            return getPerMilRank(
                this.widgetData[this.valueType]["thumbnails"].data,
                999
            );
        },
        thumbnail: function () {
            if (!this.widgetData || !this.widgetData[this.valueType]) {
                return;
            }
            if (this.selectedCluster !== undefined) {
                return {
                    data: select_3d_along_first_axis(
                        this.widgetData[this.valueType]["thumbnails"].data,
                        this.widgetData[this.valueType]["thumbnails"].shape,
                        this.selectedCluster
                    ),
                    shape: this.widgetData[this.valueType][
                        "thumbnails"
                    ].shape.slice(1),
                    dtype: "float32",
                };
            }
        },
        clusterCounts: function () {
            if (!this.widgetData || !this.widgetData[this.valueType]) {
                return;
            }
            // count how many of which cluster are there
            let clusterCounts = new Map();
            for (let cluster_id of this.widgetData[this.valueType][
                "cluster_ids"
            ]["data"]) {
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
        embeddingData: function () {
            if (!this.widgetData || !this.widgetData[this.valueType]) {
                return;
            }
            if (this.selectedCluster === undefined) {
                return {
                    data: flatten(
                        rectBin(
                            this.size,
                            this.widgetData[this.valueType]["embedding"].data,
                            undefined,
                            this.aggregationType
                        )
                    ),
                    shape: [this.size, this.size],
                    dtype: "float32",
                };
            }
            let overlayClusters = this.widgetData[this.valueType][
                "cluster_ids"
            ]["data"].map((el) => {
                if (el === this.selectedCluster) {
                    return 99999999;
                }
                return 1;
            });
            return {
                data: flatten(
                    rectBin(
                        this.size,
                        this.widgetData[this.valueType]["embedding"].data,
                        overlayClusters,
                        "mean"
                    )
                ),
                shape: [this.size, this.size],
                dtype: "float32",
            };
        },
    },
    methods: {
        handleDragStart: function (e) {
            /*
                Needs to be overriden to remove thumbnail
            */
            // remove thumbnail
            this.showTooltip = false;
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
        startDatasetSelection: function () {
            this.expectSelection = true;
            // get datasets from store
            let datasets = this.$store.state.datasets.filter((el) =>
                Object.keys(this.datasets).includes(String(el.id))
            );
            let preselection = this.selectedDataset
                ? [this.selectedDataset]
                : [];
            EventBus.$emit(
                "show-select-dialog",
                datasets,
                "cooler",
                preselection
            );
        },
        registerSelectionEventHandlers: function () {
            EventBus.$on("dataset-selected", this.handleDataSelection);
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion);
        },
        removeSelectionEventHandlers: function () {
            EventBus.$off("dataset-selected", this.handleDataSelection);
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion);
        },
        handleDataSelection: function (id) {
            if (this.expectSelection) {
                this.selectedDataset = id;
                this.expectSelection = false;
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
        selectCluster: function (x, y, visualizationSize) {
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
        hanldeSelectionAbortion: function () {
            this.expectSelection = false;
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
        handleHeatmapClick: function (x, y, adjustedX, adjustedY) {
            if (this.showTooltipControls) {
                this.showTooltipControls = false;
            } else if (this.thumbnail) {
                this.showTooltipControls = true;
            }
        },
        handleMouseMove: function (x, y, adjustedX, adjustedY, size) {
            if (!this.showTooltipControls) {
                this.showTooltip = true;
                this.tooltipOffsetLeft = adjustedX + 60;
                this.tooltipOffsetTop = adjustedY;
                this.selectCluster(x, y, size);
            }
        },
        handleMouseEnter: function (x, y, adjustedX, adjustedY) {
            if (!this.showTooltipControls) {
                this.showTooltip = true;
                this.tooltipOffsetLeft = adjustedX + 60;
                this.tooltipOffsetTop = adjustedY;
            }
        },
        handleMouseLeftTooltip: function () {
            if (!this.showTooltipControls) {
                this.showTooltip = false;
            }
        },
        handleMouseLeftContainer: function () {
            if (!this.showTooltipControls) {
                this.selectedCluster = undefined;
            }
        },
        closeControls: function () {
            this.selectedCluster = undefined;
            this.showTooltipControls = false;
            this.showTooltip = false;
        },
        resetThumbnail: function () {
            this.selectedCluster = undefined;
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
                isICCF: this.isICCF,
                isLog: this.isLog,
                widgetType: "Embedding2D",
                minHeatmap: this.minHeatmap,
                maxHeatmap: this.maxHeatmap,
                minHeatmapRange: this.minHeatmapRange,
                maxHeatmapRange: this.maxHeatmapRange,
                selectedCluster: this.selectedCluster,
                clusterNumber: this.clusterNumber,
                shareValueScale: this.shareValueScale,
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
                regionName: collectionData["regionName"],
                emptyClass: ["smallMargin", "empty"],
                isICCF: true,
                isLog: true,
                binsizes: {},
                datasets:
                    collectionData["datasetsForIntervalSize"]["embedding2d"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                minHeatmap: undefined,
                maxHeatmap: undefined,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined,
                loading: false,
                selectedCluster: undefined,
                clusterNumber: "small",
                showTooltip: false,
                showTooltipControls: false,
                tooltipOffsetTop: 0,
                tooltipOffsetLeft: 0,
                shareValueScale: false,
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
                "compare/decrement_usage_dataset",
                this.selectedDataset
            );
        },
        initializeFromStore: function (widgetData, collectionConfig) {
            var widgetDataValues;
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                // deinfe store queries
                var queryICCF = {
                    id: widgetData["widgetDataRef"]["ICCF"],
                    valueType: "ICCF",
                };
                var queryObsExp = {
                    id: widgetData["widgetDataRef"]["ObsExp"],
                    valueType: "ObsExp",
                };
                // get widget data from store
                widgetDataValues = {
                    ICCF: this.$store.getters[
                        "compare/getWidgetDataEmbedding2d"
                    ](queryICCF),
                    ObsExp: this.$store.getters[
                        "compare/getWidgetDataEmbedding2d"
                    ](queryObsExp),
                };
            } else {
                widgetDataValues = undefined;
            }
            // increment dataset usage in store. TODO: these are collections!
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
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalSize: collectionConfig["intervalSize"],
                regionName: collectionConfig["regionName"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets:
                    collectionConfig["datasetsForIntervalSize"]["embedding2d"],
                isICCF: widgetData["isICCF"],
                isLog: widgetData["isLog"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                minHeatmap: widgetData["minHeatmap"],
                maxHeatmap: widgetData["maxHeatmap"],
                minHeatmapRange: widgetData["minHeatmapRange"],
                maxHeatmapRange: widgetData["maxHeatmapRange"],
                loading: false,
                selectedCluster: widgetData["selectedCluster"],
                clusterNumber: widgetData["clusterNumber"],
                showTooltip: false,
                showTooltipControls: false,
                tooltipOffsetTop: 0,
                tooltipOffsetLeft: 0,
                shareValueScale: widgetData["shareValueScale"],
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
        getEmbeddingData: async function (valueType, id) {
            // checks whether association data is in store and fetches it if it is not
            var queryObject = {
                id: id,
                valueType: valueType,
            };
            if (
                this.$store.getters["compare/embedding2dDataExists"](
                    queryObject
                )
            ) {
                return this.$store.getters["compare/getWidgetDataEmbedding2d"](
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
                    valueType: valueType,
                };
                this.$store.commit(
                    "compare/setWidgetDataEmbedding2d",
                    mutationObject
                );
            }
            // return it
            return response.data;
        },
        updateData: async function () {
            this.loading = true;
            // construct data ids to be fecthed
            var iccf_id =
                this.binsizes[this.selectedBinsize]["ICCF"][this.clusterNumber];
            var obs_exp_id =
                this.binsizes[this.selectedBinsize]["Obs/Exp"][
                    this.clusterNumber
                ];
            // store widget data ref
            this.widgetDataRef = {
                ICCF: iccf_id,
                ObsExp: obs_exp_id,
            };
            // fetch data
            let iccf_data = await this.getEmbeddingData("ICCF", iccf_id);
            let obs_exp_data = await this.getEmbeddingData(
                "ObsExp",
                obs_exp_id
            );
            this.widgetData = {
                ICCF: iccf_data,
                ObsExp: obs_exp_data,
            };
            // reset color scale
            this.resetColorScale();
            this.resetThumbnail();
            this.loading = false;
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
                        "datasetsForIntervalSize"
                    ]["embedding2d"];
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
        intervalSize: function (newVal, oldVal) {
            // if interval size changes, reload data
            if (!newVal || !oldVal || this.selectedDataset.length == 0) {
                return;
            }
            this.binsizes =
                this.datasets[this.selectedDataset]["data_ids"][
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
            // add dataset to store for tallying used_datasets
            this.$store.commit("compare/decrement_usage_dataset", oldVal);
            this.$store.commit("compare/increment_usage_dataset", newVal);
        },
        selectedBinsize: async function () {
            if (!this.selectedBinsize) {
                return;
            }
            this.updateData();
        },
        clusterNumber: function () {
            if (!this.selectedBinszie) {
                this.updateData();
            }
        },
    },
    mounted: function () {
        this.registerSelectionEventHandlers();
    },
    beforeDestroy: function () {
        this.removeSelectionEventHandlers();
    },
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
