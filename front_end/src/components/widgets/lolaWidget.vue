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
                <div class="md-layout-item md-size-5 toggle-paired-buttons">
                    <div v-if="isBedpeFile" class="no-padding-top md-icon-button">
                        <md-button class="md-icon" :class="{'md-primary': selectedSide == 'left'}"  @click="togglePairedSides('left')">
                            <md-icon>looks_one</md-icon>
                            <md-tooltip md-direction="top" md-delay="300">
                                Plot left support data
                            </md-tooltip>
                        </md-button>
                    </div>
                </div>
                <div class="md-layout-item md-size-10 toggle-paired-buttons">
                    <div v-if="isBedpeFile" class="no-padding-top">
                        <md-button class="md-icon md-mini" :class="{'md-primary': selectedSide == 'right'}" @click="togglePairedSides('right')" style="margin-left: 8px">
                            <md-icon>looks_two</md-icon>
                        </md-button>
                            <md-tooltip md-direction="top" md-delay="300">
                                Plot right support data
                            </md-tooltip>
                    </div>
                </div>
                <div class="md-layout-item md-size-10"/>
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
            <associationPlot
                v-if="showData"
                :plotData="widgetData"
                :width="visualizationWidth"
                :height="visualizationHeight"
                :collectionNames="datasetNames"
                :intervalSize="Number(intervalSize)"
                :selectedColumn="selectedColumn"
                :binsize="Number(selectedBinsize)"
                @barclick="handleLocationChange"
            />
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
import associationPlot from "../visualizations/associationPlot";
import { apiMixin, formattingMixin, widgetMixin } from "../../mixins";
import EventBus from "../../eventBus";
export default {
    name: "lolaWidget",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    components: {
        associationPlot
    },
    computed: {
        message: function() {
            return (
                this.datasets[this.selectedDataset]["name"] +
                " | binsize " +
                this.getBinSizeFormat(this.selectedBinsize)
            );
        },
        datasetNames: function() {
            return this.datasets[this.selectedDataset][
                "collection_dataset_names"
            ];
        },
        visualizationWidth: function() {
            return Math.round(this.width * 0.9);
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
                "regions",
                preselection
            );
        },
        togglePairedSides: function(side) {
            this.selectedSide = side
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
        handleLocationChange: function(index) {
            this.selectedColumn = index;
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
                widgetType: "Lola",
                selectedColumn: this.selectedColumn,
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
                datasets: collectionData["datasetsForIntervalSize"]["lola"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                selectedColumn: undefined,
                selectedSide: 'left',
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
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                // deinfe store queries
                var payload = {
                    id: widgetData["widgetDataRef"]
                };
                // get widget data from store
                var widgetDataValues = this.$store.getters[
                    "compare/getWidgetDataLola"
                ](payload);
            } else {
                widgetDataValues = undefined;
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
                isBedpeFile: collectionConfig['isPairedEnd'],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: collectionConfig["datasetsForIntervalSize"]["lola"],
                showMenu: false,
                showDatasetSelection: false,
                showBinSizeSelection: false,
                selectedColumn: widgetData["selectedColumn"],
                selectedSide: widgetData["selectedSide"] !== undefined ? widgetData["selectedSide"] : 'left',
            };
        },
        getLolaData: async function(id) {
            // checks whether association data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (
                this.$store.getters["compare/associationDataExists"](
                    queryObject
                )
            ) {
                return this.$store.getters["compare/getWidgetDataLola"](
                    queryObject
                );
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(
                `associationIntervalData/${id}/`
            );
            // save it in store
            var mutationObject = {
                id: id,
                data: response.data
            };
            this.$store.commit("compare/setWidgetDataLola", mutationObject);
            // return it
            return response.data;
        },
        updateData: async function() {
            // construct data ids to be fecthed
            let selected_id;
            if (this.isBedpeFile){
                selected_id = this.binsizes[this.selectedBinsize][this.selectedSide];
            }else{
                selected_id = this.binsizes[this.selectedBinsize];
            }
            // store widget data ref
            this.widgetDataRef = selected_id;
            // fetch data
            this.widgetData = await this.getLolaData(selected_id);
            // blank selected column
            this.selectedColumn = undefined;
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
                    ]["lola"];
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
        selectedSide: async function() {
            if (! this.selectedSide){
                return
            }
            this.updateData()
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