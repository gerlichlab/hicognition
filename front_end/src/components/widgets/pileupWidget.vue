<template>
    <div>
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
                                v-for=" (item, id) in datasets"
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
                    <md-menu :md-offset-x="50" :md-offset-y="-36" md-size="small" :md-active.sync="showMenu">
                        <div class="padding-top-large">
                            <md-button class="md-icon-button" md-menu-trigger >
                                <md-icon>menu_open</md-icon>
                            </md-button>
                        </div>
                        <md-menu-content>
                            <md-list-item md-expand >
                            <span class="md-body-1">Scale</span>

                            <md-list slot="md-expand">
                                <md-list-item class="md-inset" @click="isICCF = true; showMenu=false" >
                                     <span class="md-body-1">ICCF</span>
                                    <md-icon
                                            v-if="isICCF"
                                            >done</md-icon
                                    >
                                </md-list-item>
                                <md-list-item class="md-inset" @click="isICCF = false; showMenu=false">
                                    <span class="md-body-1">Obs/Exp</span>
                                    <md-icon
                                            v-if="!isICCF"
                                            >done</md-icon
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
                            @click="deleteWidget"
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
                :width="pileupWidth"
                :height="pileupHeight"
                :sliderHeight="sliderHeight"
                :stackupData="widgetData[pileupType]"
                :colormap="colormap"
                :minHeatmapValue="minHeatmap"
                :maxHeatmapValue="maxHeatmap"
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
        </div>
    </div>
</template>

<script>
import heatmap from "../visualizations/heatmap";
import { apiMixin, formattingMixin } from "../../mixins";
import EventBus from "../../eventBus";

const TOOLBARHEIGHT = 71;

export default {
    name: "pileupWidget",
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
        pileupHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT ) * 0.8)
        },
        pileupWidth: function() {
            return Math.round(this.width * 0.7)
        },
        sliderHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT ) * 0.07)
        },
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
        showData: function() {
            if (this.widgetData) {
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
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            };
        }
    },
    methods: {
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
                isICCF: this.isICCF,
                widgetType: "Pileup",
                minHeatmap: this.minHeatmap,
                maxHeatmap: this.maxHeatmap
            };
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
            this.$store.commit("compare/decrement_usage_dataset", this.selectedDataset)
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
                (newCollectionData["regionID"] !=
                oldCollectionData["regionID"]) || 
                (newCollectionData["intervalSize"] !=
                oldCollectionData["intervalSize"])
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
                datasets: collectionData["availableData"]["pileup"],
                minHeatmap: undefined,
                maxHeatmap: undefined,
                isICCF: true,
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
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                minHeatmap: undefined,
                maxHeatmap: undefined,
                datasets: this.$store.getters.getCoolersDirty,
                isICCF: true,
                showMenu: false
            };
        },
        initializeAtSameCollection: function(widgetData, collectionConfig) {
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
            if (widgetData["dataset"]){
                let datasetId = widgetData["dataset"]
                this.$store.commit("compare/increment_usage_dataset", datasetId)
            }
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
        updatedData: async function(){
            // triggers load and storing of both pileuptypes
            // reset min and max colormap values
            this.minHeatmap = undefined, this.maxHeatmap = undefined;
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
        }
    },
    watch: {
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue) {
                // update availability object
                this.datasets = newValue[this.collectionID]["collectionConfig"]["availableData"]["pileup"]
                this.intervalSize = newValue[this.collectionID]["collectionConfig"]["intervalSize"]
            }
        },
        datasets: function(oldVal, newVal){
            if (!newVal || !oldVal || !this.selectedDataset){
                return
            }
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][this.intervalSize]
            let binsizes = Object.keys(this.binsizes)
            this.selectedBinsize = Number(binsizes[Math.floor(binsizes.length / 2)])
            this.updatedData()
        },
        intervalSize: function(newVal, oldVal){
            // if interval size changes, reload data
            if (!newVal || !oldVal || !this.selectedDataset){
                return
            }
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][this.intervalSize]
            let binsizes = Object.keys(this.binsizes)
            this.selectedBinsize = Number(binsizes[Math.floor(binsizes.length / 2)])
            this.updatedData()
        },
        selectedDataset: function(newVal, oldVal) {
            if (!this.selectedDataset) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // reset min and max colormap values
            this.minHeatmap = undefined, this.maxHeatmap = undefined;
            // set binsizes from available datasets 
            this.binsizes = this.datasets[this.selectedDataset]["data_ids"][this.intervalSize]
            let binsizes = Object.keys(this.binsizes)
            if (!this.selectedBinsize){
                this.selectedBinsize = Number(binsizes[Math.floor(binsizes.length / 2)])
            }else{
                this.updatedData()
            }
            this.$store.commit("compare/decrement_usage_dataset", oldVal)
            this.$store.commit("compare/increment_usage_dataset", newVal)

        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            this.updatedData()
        },
        isICCF: function() {
            // reset min and max when this changes
            this.minHeatmap = undefined;
            this.maxHeatmap = undefined;
        }
    },
    mounted: function (){
        EventBus.$on('serialize-widgets', this.serializeWidget)
        // widget deletion can be trigered via event bus from widget collection
        EventBus.$on('delete-widget', (id) => {
            if (id == this.id){
                this.deleteWidget()
            }
        })
    },
    beforeDestroy: function(){
        EventBus.$off('serialize-widgets')
        // delete widget does not need to be taken off the event bus as ids don't get reused
    }
};
</script>

<style scoped>
.bg {
    background-color: rgba(211, 211, 211, 0.2);
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
