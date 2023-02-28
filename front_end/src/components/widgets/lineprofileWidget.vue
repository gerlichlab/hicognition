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
                    class="md-layout-item md-size-15 padding-left"
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
                        <md-button class="md-icon" :class="{'md-primary': selectedSide == 'left'}"  @click="togglePairedSides('left')">
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
                        <md-button class="md-icon md-mini" :class="{'md-primary': selectedSide == 'right'}" @click="togglePairedSides('right')" style="margin-left: 8px">
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
                                <span class="md-body-1">Scale</span>

                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            normalized = false;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1">Unscaled</span>
                                        <md-icon v-if="!normalized"
                                            >done</md-icon
                                        >
                                    </md-list-item>
                                    <md-list-item
                                        class="md-inset"
                                        @click="
                                            normalized = true;
                                            showMenu = false;
                                        "
                                    >
                                        <span class="md-body-1"
                                            >Normalized</span
                                        >
                                        <md-icon v-if="normalized"
                                            >done</md-icon
                                        >
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
                            <md-list-item
                                md-expand
                                v-if="
                                    allowBinsizeSelection &&
                                        !valueScaleRecipient
                                "
                            >
                                <span class="md-body-1">Value range</span>
                                <md-list slot="md-expand">
                                    <div class="padding">
                                        <md-field>
                                            <label>Max</label>
                                            <md-input
                                                v-model="maxTarget"
                                                type="number"
                                            ></md-input>
                                        </md-field>
                                        <md-field>
                                            <label>Min</label>
                                            <md-input
                                                v-model="minTarget"
                                                type="number"
                                            ></md-input>
                                        </md-field>
                                        <div class="float-left">
                                            <md-button
                                                class="md-raised"
                                                @click="
                                                    handleValueScaleTargetReset
                                                "
                                                :disabled="ignoreTarget"
                                                >Reset</md-button
                                            >
                                        </div>
                                        <div class="float-right">
                                            <md-button
                                                class="md-raised md-primary"
                                                @click="
                                                    handleValueScaleTargetSet
                                                "
                                                >Set</md-button
                                            >
                                        </div>
                                    </div>
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
            <lineprofile
                v-if="showData"
                :lineprofileID="id"
                :width="visualizationWidth"
                :height="lineprofileHeight"
                :lineprofileNames="lineProfileNames"
                :lineprofileData="widgetData"
                :normalized="normalized"
                :showInterval="isVariableSize"
                :valueScaleColor="valueScaleColor"
                :valueScaleBorder="valueScaleBorder"
                :minValueRange="
                    minHeatmapRange === undefined
                        ? minHeatmapRange
                        : Number(minHeatmapRange)
                "
                :maxValueRange="
                    maxHeatmapRange === undefined
                        ? maxHeatmapRange
                        : Number(maxHeatmapRange)
                "
                @value-scale-change="handleValueScaleChange"
            >
            </lineprofile>
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
import lineprofile from "../visualizations/lineprofile";
import {
    apiMixin,
    formattingMixin,
    widgetMixin,
    valueScaleSharingMixin
} from "../../mixins";
import EventBus from "../../eventBus";

export default {
    name: "lineprofileWidget",
    mixins: [apiMixin, formattingMixin, widgetMixin, valueScaleSharingMixin],
    components: {
        lineprofile
    },
    computed: {
        visualizationWidth: function() {
            return this.width;
        },
        lineprofileHeight: function() {
            // needs to be adjusted because is not square like heatmap using widgets
            return this.visualizationHeight - 10;
        },
        message: function() {
            let datasetSummary = "";
            for (let selected of this.selectedDataset) {
                let name = this.datasets[selected]["name"];
                datasetSummary += name + " | ";
            }
            if (datasetSummary.length > 40) {
                datasetSummary = "multiple datasets | ";
            }
            datasetSummary = datasetSummary +
                "binsize " +
                this.getBinSizeFormat(this.selectedBinsize);
            
            return datasetSummary;
        }
    },
    methods: {
        handleValueScaleTargetSet() {
            this.ignoreTarget = false;
            this.minHeatmapRange = this.minTarget;
            this.maxHeatmapRange = this.maxTarget;
        },
        handleValueScaleTargetReset() {
            this.ignoreTarget = true;
            this.minHeatmapRange = this.minTarget = undefined;
            this.maxHeatmapRange = this.maxTarget = undefined;
        },
        togglePairedSides: function(side) {
            this.selectedSide = side
        },
        setColorScale: function(data) {
            /* 
                sets colorScale based on data array
                containing minPos, maxPos, minRange, maxRange
            */
            if (this.ignoreTarget) {
                this.minHeatmap = data[0];
                this.maxHeatmap = data[1];
                this.minHeatmapRange = data[2];
                this.maxHeatmapRange = data[3];
                this.minTarget = Math.round(data[2] * 10 ** 5) / 10 ** 5;
                this.maxTarget = Math.round(data[3] * 10 ** 5) / 10 ** 5;
            } else {
                this.minHeatmapRange = this.minTarget;
                this.maxHeatmapRange = this.maxTarget;
            }
        },
        handleValueScaleChange: function(data) {
            if (!this.valueScaleRecipient) {
                this.setColorScale(data);
                this.broadcastValueScaleUpdate();
            }
        },
        handleWidgetSelection: function() {
            if (this.allowValueScaleTargetSelection) {
                this.handleWidgetValueScaleSelection();
            }
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
        blankWidget: function() {
            // removes all information that the user can set in case a certain region/dataset combination is not available
            this.widgetData = undefined;
            this.selectedDataset = [];
            this.selectedBinsize = undefined;
            this.widgetDataRef = undefined;
        },
        startDatasetSelection: function() {
            this.expectSelection = true;
            // get datasets from store
            let datasets = this.$store.state.datasets.filter(el =>
                Object.keys(this.datasets).includes(String(el.id))
            );
            let preselection = this.selectedDataset
                ? [...this.selectedDataset]
                : [];
            EventBus.$emit(
                "show-select-dialog",
                datasets,
                "bigwig",
                preselection,
                false
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
        handleDataSelection: function(ids) {
            if (this.expectSelection) {
                this.selectedDataset = ids;
                this.expectSelection = false;
            }
        },
        hanldeSelectionAbortion: function() {
            this.expectSelection = false;
        },
        handleBinsizeSelection: function(binsize) {
            this.selectedBinsize = binsize;
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
            this.prepareDeletionValueScale();
            this.deleteWidget();
        },
        deleteWidget: function() {
            // release color
            if (this.sortOrderRecipients > 0) {
                this.$store.commit("releaseColorUsage", this.sortOrderColor);
            }
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
                lineProfileNames: this.lineProfileNames,
                isDefault: this.isDefault,
                minHeatmap: this.minHeatmap,
                maxHeatmap: this.maxHeatmap,
                minHeatmapRange: this.minHeatmapRange,
                maxHeatmapRange: this.maxHeatmapRange,
                valueScaleRecipient: this.valueScaleRecipient,
                valueScaleRecipients: this.valueScaleRecipients,
                valueScaleTargetID: this.valueScaleTargetID,
                valueScaleColor: this.valueScaleColor,
                widgetType: "Lineprofile",
                normalized: this.normalized,
                minTarget: this.minTarget,
                maxTarget: this.maxTarget,
                ignoreTarget: this.ignoreTarget,
                selectedSide: this.selectedSide,
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
                isBedpeFile: collectionData['isPairedEnd'],
                emptyClass: ["smallMargin", "empty"],
                binsizes: {},
                datasets:
                    collectionData["datasetsForIntervalSize"]["lineprofile"],
                isDefault: true,
                lineProfileNames: [],
                showMenu: false,
                normalized: false,
                reactToUpdate: true, // whether to react to updates in binsize/dataset
                showDatasetSelection: false,
                showBinSizeSelection: false,
                expectSelection: false,
                minHeatmap: 0, // these values have no meaning, they are for compatibility with the valuescale mixin
                maxHeatmap: 0, // these values have no meaning, they are for compatibility with the valuescale mixin
                valueScaleRecipient: false,
                valueScaleRecipients: 0,
                valueScaleSelectionState: false,
                valueScaleTargetID: false,
                valueScaleColor: undefined,
                expectingValueScale: false,
                minHeatmapRange: undefined,
                maxHeatmapRange: undefined,
                showSelection: false,
                colormap: null, // this value have no meaning, they are for compatibility with the valuescale mixin
                minTarget: undefined,
                maxTarget: undefined,
                ignoreTarget: true,
                selectedSide: 'left',
            };
            // write properties to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            return data;
        },
        initializeFromStore: function(widgetData, collectionConfig) {
            var widgetDataValues;
            let selectedSide = widgetData["selectedSide"] !== undefined ? widgetData["selectedSide"] : 'left';
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                var widgetDataRef = widgetData["widgetDataRef"];
                var widgetDataValues = [];
                for (var widget_data_id of widgetDataRef) {
                    //
                    if (collectionConfig['isPairedEnd']){
                        var payload = {
                            id: widget_data_id[selectedSide]
                        };
                    }else{
                        // deinfe store queries
                        var payload = {
                            id: widget_data_id
                        };
                    }
                    // get widget data from store
                    var new_widgetDataValues = this.$store.getters[
                        "compare/getWidgetDataLineprofile"
                    ](payload);
                    widgetDataValues.push(new_widgetDataValues);
                }
            } else {
                widgetDataValues = undefined;
            }
            // increment dataset usage in store
            if (widgetData["dataset"]) {
                for (let datasetId of widgetData["dataset"]) {
                    this.$store.commit(
                        "compare/increment_usage_dataset",
                        datasetId
                    );
                }
            }
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                isBedpeFile: collectionConfig['isPairedEnd'],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                lineProfileNames: widgetData["lineProfileNames"],
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets:
                    collectionConfig["datasetsForIntervalSize"]["lineprofile"],
                isDefault: widgetData["isDefault"],
                showMenu: false,
                normalized: widgetData["normalized"],
                showDatasetSelection: false,
                showBinSizeSelection: false,
                expectSelection: false,
                reactToUpdate: false,
                minHeatmap: 0, // this value have no meaning, they are for compatibility with the valuescale mixin
                maxHeatmap: 0, // this value have no meaning, they are for compatibility with the valuescale mixin
                minHeatmapRange:
                    widgetData["minHeatmapRange"] !== undefined
                        ? widgetData["minHeatmapRange"]
                        : undefined,
                maxHeatmapRange:
                    widgetData["maxHeatmapRange"] !== undefined
                        ? widgetData["maxHeatmapRange"]
                        : undefined,
                valueScaleSelectionState: false,
                valueScaleRecipient:
                    widgetData["valueScaleRecipient"] !== undefined
                        ? widgetData["valueScaleRecipient"]
                        : false,
                valueScaleRecipients:
                    widgetData["valueScaleRecipients"] !== undefined
                        ? widgetData["valueScaleRecipients"]
                        : 0,
                valueScaleTargetID:
                    widgetData["valueScaleTargetID"] !== undefined
                        ? widgetData["valueScaleTargetID"]
                        : false,
                valueScaleColor:
                    widgetData["valueScaleColor"] !== undefined
                        ? widgetData["valueScaleColor"]
                        : undefined,
                showSelection: false,
                colormap: null, // this value have no meaning, they are for compatibility with the valuescale mixin
                minTarget:
                    widgetData["minTarget"] !== undefined
                        ? widgetData["minTarget"]
                        : true,
                maxTarget:
                    widgetData["maxTarget"] !== undefined
                        ? widgetData["maxTarget"]
                        : true,
                ignoreTarget:
                    widgetData["ignoreTarget"] !== undefined
                        ? widgetData["ignoreTarget"]
                        : true,
                selectedSide: widgetData["selectedSide"] !== undefined ? widgetData["selectedSide"] : 'left',
            };
        },
        getlineprofileData: async function(id) {
            // checks whether lineprofile data is in store and fetches it if it is not
            if (this.$store.getters["compare/lineprofileExists"](id)) {
                return this.$store.getters["compare/getWidgetDataLineprofile"](
                    id
                );
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(`averageIntervalData/${id}/`);
            var parsed = response.data;
            // save it in store
            var mutationObject = {
                id: id,
                data: parsed
            };
            this.$store.commit(
                "compare/setWidgetDataLineprofile",
                mutationObject
            );
            // return it
            return parsed;
        },
        updateData: async function() {
            // construct data ids to be fecthed
            // reset min and max colormap values if not value scale recipient
            if (!this.valueScaleRecipient) {
                this.resetColorScale();
            }
            let selected_ids = this.binsizes[this.selectedBinsize];
            // store widget data ref
            this.widgetDataRef = selected_ids;
            
            // prepare line data and names
            var lineData = [];
            var lineNames = [];
            for (let i = 0; i < selected_ids.length; i++) {
                let data_id;
                if (this.isBedpeFile){
                    data_id = selected_ids[i][this.selectedSide]
                }else{
                    data_id = selected_ids[i]
                }
                let data = await this.getlineprofileData(data_id);
                let name = this.datasets[this.selectedDataset[i]]["name"];
                lineData.push(data);
                lineNames.push(name)
            }

            this.widgetData = lineData;
            this.lineProfileNames = lineNames;
            //broadcast value scale update
            this.broadcastValueScaleUpdate();
        },
        getIdsOfBinsizes: function() {
            // takes selected dataset array and constructs an object with binsizes and arrays of data ids
            let binsizes = {};
            for (let selectedDataset of this.selectedDataset) {
                let temp_binsizes = this.datasets[selectedDataset]["data_ids"][
                    this.intervalSize
                ];
                // if temp binsizes is undefined, there is no data for these binsizes -> return undefined to blank widget
                if (temp_binsizes === undefined) {
                    return undefined;
                }
                for (let [key, value] of Object.entries(temp_binsizes)) {
                    if (!(key in binsizes)) {
                        binsizes[key] = [value];
                    } else {
                        binsizes[key].push(value);
                    }
                }
            }
            return binsizes;
        },
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
                    ]["lineprofile"];
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
                this.selectedDataset.length == 0 ||
                !this.reactToUpdate
            ) {
                // switch on react to update
                this.reactToUpdate = true;
                return;
            }
            // check whether there is data available
            for (let testDataset of this.selectedDataset) {
                if (!this.datasets[testDataset]) {
                    this.blankWidget();
                    return;
                }
            }
            this.binsizes = this.getIdsOfBinsizes();
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
            this.binsizes = this.getIdsOfBinsizes();
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
            // set binsizes -> there can be multiple datasets, binsizes need to be collected for them
            this.binsizes = this.getIdsOfBinsizes();
            // check whether binsizes are defined
            if (this.binsizes === undefined) {
                // not data exists, blank widget DAta
                this.widgetData = undefined;
                return;
            }
            // remove old dataset ids from used values in store
            for (let dataset_id_old of oldVal) {
                this.$store.commit(
                    "compare/decrement_usage_dataset",
                    dataset_id_old
                );
            }
            // add new datasets to used values in store
            for (let dataset_id_new of newVal) {
                this.$store.commit(
                    "compare/increment_usage_dataset",
                    dataset_id_new
                );
            }
            // if no binsizes selected, set default and return
            if (!this.selectedBinsize) {
                this.selectedBinsize = this.getCenterOfArray(
                    Object.keys(this.binsizes)
                );
            } else {
                this.updateData();
            }
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            this.updateData();
        },
        selectedSide: async function() {
            if (! this.selectedSide){
                return
            }
            this.updateData()
        }
    },
    mounted: function() {
        this.registerSelectionEventHandlers();
        this.registerValueScaleEventHandlers();
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

.padding {
    padding: 10px;
}

.float-left {
    float: left;
}

.float-right {
    float: right;
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
