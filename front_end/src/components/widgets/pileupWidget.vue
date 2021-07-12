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
                    class="md-layout-item md-size-30 padding-left padding-right"
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
                    class="md-layout-item md-size-30 padding-left padding-right"
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
                        :md-offset-x="50"
                        :md-offset-y="-36"
                        md-size="small"
                        :md-active.sync="showMenu"
                    >
                        <div class="padding-top-large">
                            <md-button class="md-icon-button" md-menu-trigger>
                                <md-icon>menu_open</md-icon>
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
                    <div class="padding-top-large padding-right">
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
                @slider-change="handleSliderChange"
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
            <div class="flex-container" v-if="showData">
            <div >
                <span class="md-caption">{{message}}</span>
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

export default {
    name: "pileupWidget",
    mixins: [apiMixin, formattingMixin, widgetMixin, valueScaleSharingMixin],
    components: {
        heatmap
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
        message: function(){
            return  this.datasets[this.selectedDataset]["name"] +  " | binsize " + this.convertBasePairsToReadable(this.selectedBinsize)
        }
    },
    methods: {
        handleColormapMissmatch: function(colormap){
            this.reactToICCFSwitch = false;
            if (colormap == "fall"){
                this.isICCF = true
            }else{
                this.isICCF = false
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
            this.setColorScale(data)
            this.broadcastValueScaleUpdate()
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
                this.$store.commit("releaseValueScaleColorUsage", this.valueScaleColor);
            }
            this.deleteWidget();
        },
        deleteWidget: function() {
            // release color
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
                datasets: collectionData["availableData"]["pileup"],
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
                resetColorScaleFlag: true
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
            this.$store.commit("setValueScaleColorUsage", widgetData["valueScaleColor"]);
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
                datasets: collectionConfig["availableData"]["pileup"],
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
                maxHeatmapRange:  widgetData["maxHeatmapRange"],
                reactToICCFSwitch: true,
                resetColorScaleFlag: false
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
            // reset min and max colormap values
            if (this.resetColorScaleFlag && !this.valueScaleTargetID){
                this.resetColorScale()
            }else{
                this.resetColorScaleFlag = true
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
                    ]["pileup"];
                this.intervalSize =
                    newValue[this.collectionID]["collectionConfig"][
                        "intervalSize"
                    ];
            }
        },
        datasets: function(oldVal, newVal) {
            if (!newVal || !oldVal || !this.selectedDataset) {
                return;
            }
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][
                this.intervalSize
            ];
            this.selectedBinsize = this.getCenterOfArray(
                Object.keys(this.binsizes)
            );
            this.updatedData();
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
            this.updatedData();
        },
        selectedDataset: function(newVal, oldVal) {
            if (!this.selectedDataset) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // reset min and max colormap values
            if (!this.valueScaleTargetID){
                (this.minHeatmap = undefined), (this.maxHeatmap = undefined);
            }
            // set binsizes from available datasets
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][
                this.intervalSize
            ];
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
            if (this.reactToICCFSwitch){
                this.resetColorScale()
            }else{
                this.reactToICCFSwitch = true
            }
        }
    },
    mounted: function(){
        this.registerValueScaleEventHandlers()
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

.height-71 {
    height: 71px;
}
</style>
