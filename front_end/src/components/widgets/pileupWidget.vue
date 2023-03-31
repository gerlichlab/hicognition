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
                                <span class="md-body-1">Scale</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            isICCF = true;
                                            showMenu = false;
                                        "
                                        :disabled="valueScaleRecipient"
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
                                        :disabled="valueScaleRecipient"
                                    >
                                        <span class="md-body-1">Obs/Exp</span>
                                        <md-icon v-if="!isICCF">done</md-icon>
                                    </md-list-item>
                                </md-list>
                            </md-list-item>
                            <md-list-item md-expand>
                                <span class="md-body-1">Share</span>
                                <md-list slot="md-expand">
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
                    <div class="no-padding-top padding-right">
                        <md-button
                            @click="handleWidgetDeletion"
                            class="md-icon-button md-accent"
                        >
                            <md-icon>delete</md-icon>
                        </md-button>
                    </div>
                </div>
            </div>
            <div style="position: relative">
                <heatmap
                    v-if="showData"
                    :pileupID="id"
                    :width="visualizationWidth"
                    :height="visualizationHeight"
                    :stackupData="widgetData[pileupType]"
                    :colormap="colormap"
                    :minHeatmapValue="minHeatmap"
                    :maxHeatmapValue="maxHeatmap"
                    :minHeatmapRange="minHeatmapRange"
                    :maxHeatmapRange="maxHeatmapRange"
                    :valueScaleColor="valueScaleColor"
                    :valueScaleBorder="valueScaleBorder"
                    :allowValueScaleChange="allowValueScaleChange"
                    :log="true"
                    :isInterval="isVariableSize"
                    :windowsize="intervalSize"
                    :showXaxis="true"
                    @slider-change="handleSliderChange"
                    @mouse-move="handleMouseMoveHeatmap"
                    @mouse-enter="handleMouseEnterHeatmap"
                    @mouse-leave="handleMouseLeftHeatmap"
                    @mouse-leave-container="handleMouseLeftHeatmapContainer"
                />
                <value-info-tooltip
                    v-if="showTooltip"
                    :message="tooltipMessage"
                    :tooltipOffsetLeft="tooltipOffsetLeft"
                    :tooltipOffsetTop="tooltipOffsetTop"
                />
            </div>
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
import EventBus from "../../eventBus";
import heatmap from "../visualizations/heatmap";
import {
    apiMixin,
    formattingMixin,
    widgetMixin,
    valueScaleSharingMixin
} from "../../mixins";
import valueInfoTooltip from "../visualizations/valueInfoTooltip.vue";

const EXPANSION_FACTOR = 0.2;

export default {
    name: "pileupWidget",
    mixins: [apiMixin, formattingMixin, widgetMixin, valueScaleSharingMixin],
    components: {
        heatmap,
        valueInfoTooltip
    },
    computed: {
        colormap: function() {
            if (this.pileupType == "ICCF") {
                return "fall";
            }
            return "blueWhiteRed";
        },
        pileupType: function() {
            if (this.isICCF) {
                return "ICCF";
            } else {
                return "ObsExp";
            }
        },
        message: function() {
            return (
                this.datasets[this.selectedDataset]["name"] +
                " | binsize " +
                this.getBinSizeFormat(this.selectedBinsize)
            );
        }
    },
    methods: {
        handleDragStart: function(e) {
            /*
                Needs to be overriden to remove tooltip
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
        translateMouseToPosition: function(x, y, size) {
            let bin_width = size / this.widgetData[this.pileupType].shape[0];
            let x_bin = Math.round(x / bin_width);
            let y_bin = Math.round(y / bin_width);
            let xoffset;
            let yoffset;
            if (this.isVariableSize) {
                let intervalSize = Math.round(
                    this.widgetData[this.pileupType].shape[0] /
                        (1 + 2 * EXPANSION_FACTOR)
                );
                let intervalStartBin = Math.round(
                    intervalSize * EXPANSION_FACTOR
                );
                // get x offset
                if (x_bin > intervalStartBin) {
                    xoffset =
                        (x_bin - intervalStartBin) *
                        Number(this.selectedBinsize);
                } else {
                    xoffset = -(
                        EXPANSION_FACTOR * 100 -
                        x_bin * Number(this.selectedBinsize)
                    );
                }
                // get y offset
                if (y_bin > intervalStartBin) {
                    yoffset =
                        (y_bin - intervalStartBin) *
                        Number(this.selectedBinsize);
                } else {
                    yoffset = -(
                        EXPANSION_FACTOR * 100 -
                        y_bin * Number(this.selectedBinsize)
                    );
                }
                return `x: ${xoffset} % | y: ${yoffset} %`;
            }
            let totalSize = Number(this.intervalSize);
            let numberBins = Math.round(
                this.widgetData[this.pileupType].shape[0]
            ); // pileup is symmetric
            let halfBins = Math.round(numberBins / 2);
            // get x offset
            if (x_bin < halfBins) {
                xoffset = -(totalSize - x_bin * Number(this.selectedBinsize));
            } else {
                xoffset = (x_bin - halfBins) * Number(this.selectedBinsize);
            }
            // get y offset
            if (y_bin < halfBins) {
                yoffset = totalSize - y_bin * Number(this.selectedBinsize);
            } else {
                yoffset = -((y_bin - halfBins) * Number(this.selectedBinsize));
            }
            return `x: ${this.convertBasePairsToReadable(
                xoffset
            )} | y: ${this.convertBasePairsToReadable(yoffset)}`;
        },
        handleMouseEnterHeatmap: function(x, y, adjustedX, adjustedY) {
            this.showTooltip = true;
            this.tooltipOffsetLeft = adjustedX + 50;
            this.tooltipOffsetTop = adjustedY;
        },
        handleMouseMoveHeatmap: function(x, y, adjustedX, adjustedY, size) {
            // only show tooltip if widget is not being dragged
            if (this.dragImage === undefined) {
                this.showTooltip = true;
                this.tooltipOffsetLeft = adjustedX + 50;
                this.tooltipOffsetTop = adjustedY;
                this.tooltipMessage = this.translateMouseToPosition(x, y, size);
            }
        },
        handleMouseLeftHeatmap: function() {
            this.showTooltip = false;
        },
        handleMouseLeftHeatmapContainer: function() {
            this.showTooltip = false;
        },
        startDatasetSelection: function() {
            this.expectSelection = true;
            // get datasets from store
            let datasets = this.$store.state.datasets.filter(el =>
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
                this.selectedDataset = id;
                this.expectSelection = false;
            }
        },
        hanldeSelectionAbortion: function() {
            this.expectSelection = false;
        },
        handleBinsizeSelection: function(binsize) {
            this.selectedBinsize = binsize;
        },
        handleColormapMissmatch: function(colormap) {
            this.reactToICCFSwitch = false;
            if (colormap == "fall") {
                this.isICCF = true;
            } else {
                this.isICCF = false;
            }
        },
        handleMouseEnter: function() {
            if (this.allowValueScaleTargetSelection) {
                this.showSelection = true;
            }
        },
        handleMouseLeave: function() {
            if (this.allowValueScaleTargetSelection) {
                this.showSelection = false;
            }
        },
        handleWidgetSelection: function() {
            if (this.allowValueScaleTargetSelection) {
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
                isICCF: this.isICCF,
                widgetType: "Pileup",
                minHeatmap: this.minHeatmap,
                maxHeatmap: this.maxHeatmap,
                valueScaleSelectionState: false,
                showSelection: false,
                valueScaleRecipient: this.valueScaleRecipient,
                valueScaleRecipients: this.valueScaleRecipients,
                valueScaleTargetID: this.valueScaleTargetID,
                valueScaleColor: this.valueScaleColor,
                minHeatmapRange: this.minHeatmapRange,
                maxHeatmapRange: this.maxHeatmapRange
            };
        },
        handleWidgetDeletion: function() {
            // needs to be separate to distinguish it from moving
            // emit events for sort-order update
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
            this.deleteWidget();
        },
        deleteWidget: function() {
            // release color
            if (this.valueScaleRecipients > 0) {
                this.$store.commit(
                    "releaseValueScaleColorUsage",
                    this.valueScaleColor
                );
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
                datasets: collectionData["datasetsForIntervalSize"]["pileup"],
                minHeatmap: undefined,
                maxHeatmap: undefined,
                isICCF: true,
                showMenu: false,
                expectingValueScale: false,
                valueScaleSelectionState: false,
                showSelection: false,
                valueScaleRecipient: false,
                valueScaleRecipients: 0,
                valueScaleTargetID: false,
                valueScaleColor: undefined,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined,
                reactToICCFSwitch: true,
                reactToUpdate: true, // whether to react to updates in binsize/dataset
                showDatasetSelection: false,
                showBinSizeSelection: false,
                expectSelection: false,
                showTooltip: false,
                tooltipOffsetTop: 0,
                tooltipOffsetLeft: 0,
                tooltipMessage: undefined
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
                var queryICCF = {
                    pileupType: "ICCF",
                    id: widgetDataRef["ICCF"]
                };
                var queryObsExp = {
                    pileupType: "ObsExp",
                    id: widgetDataRef["ObsExp"]
                };
                // get widget data from store
                widgetDataValues = {
                    ICCF: this.$store.getters["compare/getWidgetDataPileup"](
                        queryICCF
                    ),
                    ObsExp: this.$store.getters["compare/getWidgetDataPileup"](
                        queryObsExp
                    )
                };
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
            this.$store.commit(
                "setValueScaleColorUsage",
                widgetData["valueScaleColor"]
            );
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                minHeatmap: widgetData["minHeatmap"],
                maxHeatmap: widgetData["maxHeatmap"],
                selectedBinsize: widgetData["binsize"],
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: collectionConfig["datasetsForIntervalSize"]["pileup"],
                isICCF: widgetData["isICCF"],
                valueScaleSelectionState: false,
                valueScaleRecipient: widgetData["valueScaleRecipient"],
                valueScaleRecipients: widgetData["valueScaleRecipients"],
                valueScaleTargetID: widgetData["valueScaleTargetID"],
                valueScaleColor: widgetData["valueScaleColor"],
                expectingValueScale: false,
                showMenu: false,
                showSelection: false,
                minHeatmapRange: widgetData["minHeatmapRange"],
                maxHeatmapRange: widgetData["maxHeatmapRange"],
                reactToICCFSwitch: true,
                reactToUpdate: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                expectSelection: false,
                showTooltip: false,
                tooltipOffsetTop: 0,
                tooltipOffsetLeft: 0,
                tooltipMessage: undefined
            };
        },
        getPileupData: async function(pileupType, id) {
            // checks whether pileup data is in store and fetches it if it is not
            var queryObject = {
                pileupType: pileupType,
                id: id
            };
            if (this.$store.getters["compare/pileupExists"](queryObject)) {
                return this.$store.getters["compare/getWidgetDataPileup"](
                    queryObject
                );
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(`averageIntervalData/${id}/`);
            var parsed = response.data;
            // save it in store
            var mutationObject = {
                pileupType: pileupType,
                id: id,
                data: parsed
            };
            this.$store.commit("compare/setWidgetDataPileup", mutationObject);
            // return it
            return parsed;
        },
        updatedData: async function() {
            // triggers load and storing of both pileuptypes
            // reset min and max colormap values if not value scale recipient
            if (!this.valueScaleRecipient) {
                this.resetColorScale();
            }
            // fetch widget data
            var iccf_id = this.binsizes[this.selectedBinsize]["ICCF"];
            var obs_exp_id = this.binsizes[this.selectedBinsize]["Obs/Exp"];
            // store widget data ref
            this.widgetDataRef = {
                ICCF: iccf_id,
                ObsExp: obs_exp_id
            };
            // get pileup iccf; update pileup data upon success
            var iccf_data = await this.getPileupData("ICCF", iccf_id);
            var obs_exp_data = await this.getPileupData("ObsExp", obs_exp_id);
            this.widgetData = {
                ICCF: iccf_data,
                ObsExp: obs_exp_data
            };
            // broadcast value scale update
            this.broadcastValueScaleUpdate();
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
                    ]["pileup"];
                this.intervalSize =
                    newValue[this.collectionID]["collectionConfig"][
                        "intervalSize"
                    ];
            }
        },
        datasets: function(oldVal, newVal) {
            if (
                !newVal ||
                !oldVal ||
                !this.selectedDataset ||
                !this.reactToUpdate
            ) {
                // switch on react to update
                this.reactToUpdate = true;
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
            this.updatedData();
        },
        intervalSize: function(newVal, oldVal) {
            // if interval size changes, reload data
            if (
                !newVal ||
                !oldVal ||
                !this.selectedDataset ||
                !this.reactToUpdate
            ) {
                this.reactToUpdate = true;
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
            this.updatedData();
        },
        selectedDataset: function(newVal, oldVal) {
            if (!this.selectedDataset) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // reset min and max colormap values
            if (!this.valueScaleTargetID) {
                (this.minHeatmap = undefined), (this.maxHeatmap = undefined);
            }
            // set binsizes from available datasets
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
                this.updatedData();
            }
            this.$store.commit("compare/decrement_usage_dataset", oldVal);
            this.$store.commit("compare/increment_usage_dataset", newVal);
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            this.updatedData();
        },
        isICCF: function() {
            // reset min and max when this changes
            if (this.reactToICCFSwitch) {
                this.resetColorScale();
            } else {
                this.reactToICCFSwitch = true;
            }
        }
    },
    mounted: function() {
        this.registerValueScaleEventHandlers();
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

.flex-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.align-text-center {
    text-align: center;
}

.padding-right {
    padding-right: 15px;
}

.padding-left {
    padding-left: 10px;
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

.toolbarheight {
    height: 40px;
}
</style>
