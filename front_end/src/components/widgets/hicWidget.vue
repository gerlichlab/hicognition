<template>
<div>
    <div :style="cssStyle" class="smallMargin md-elevation-1 bg" draggable="true" @dragstart="handleDragStart">
        <div class="md-layout">
            <div class="md-layout-item md-size-30 padding-left padding-right">
                <md-field class="padding-top">
                        <md-select
                        v-model="selectedDataset"
                        name="dataset"
                        id="dataset"
                        placeholder="Dataset"
                        :disabled="!allowDatasetSelection"
                        >
                        <md-option
                            v-for="item in datasets"
                            :value="item.id"
                            :key="item.id"
                            >{{ item.dataset_name }}</md-option
                        >
                        </md-select>
                </md-field>
            </div>
            <div class="md-layout-item md-size-30 padding-left padding-right">
                <md-field class="padding-top">
                        <md-select
                        v-model="selectedBinsize"
                        name="binsize"
                        id="binsze"
                        placeholder="Binsize"
                        :disabled="!allowBinsizeSelection"
                        >
                        <md-option
                            v-for="item in binsizes"
                            :value="item.binsize"
                            :key="item.binsize"
                            >{{ item.binsize }}</md-option
                        >
                        </md-select>
                </md-field>
            </div>
            <div class="md-layout-item md-size-25">
                <div class="padding-top">
                    <md-switch v-model="isICCF">{{ pileupType }}</md-switch>
                </div>
            </div>
            <div class="md-layout-item md-size-10">
                <div class="padding-top-large padding-right">
                  <md-button  @click="deleteWidget"  class="md-icon-button md-accent">
                    <md-icon>delete</md-icon>
                 </md-button>
                </div>
            </div>
        </div>
        <pileup
            title="Obs/Exp"
            :pileupType="pileupType"
            v-if="showData"
            :pileupID="id"
            :width="225"
            :height="225"
            :pileupData="widgetData[pileupType]"
            :log="true" >
        </pileup>
        <div v-if="!showData" class="md-layout md-alignment-center-center" style="height: 70%;">
                <md-icon class="md-layout-item md-size-50 md-size-5x">input</md-icon>
        </div>
    </div>
</div>
</template>

<script>
import pileup from "../pileup";
import { apiMixin } from "../../mixins";
import { group_iccf_obs_exp } from "../../functions";

export default {
    name: 'hiCWidget',
    mixins: [apiMixin],
    components: {
        pileup
    },
    data: function () {
        // get widget data from store for initialization
        return this.initializeWidget()
    },
    props: {
        width: Number,
        height: Number,
        empty: Boolean,
        id: Number,
        collectionID: Number,
        rowIndex: Number,
        colIndex: Number,
    },
    computed:{
        pileupType: function() {
            if (this.isICCF){
                return "ICCF"
            }else{
                return "ObsExp"
            }
        },
        showData: function() {
            if (this.widgetData){
                return true
            }
            return false
        },
        allowDatasetSelection: function() {
            if (this.intervalID){
                return true
            }
            return false
        },
        allowBinsizeSelection: function() {
            return this.binsizes.length != 0
        },
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            }
        }
    },
    methods: {
        toStoreObject: function(){
            // serialize object for storing its state in the store
            return {
                // collection Data is needed if widget is dropped on new collection
                collectionData: this.$store.getters["compare/getCollectionProperties"](this.collectionID),
                colIndex: this.colIndex,
                rowIndex: this.rowIndex,
                id: this.id,
                parentID: this.collectionID,
                dataset: this.selectedDataset,
                datasets: this.datasets,
                binsizes: this.binsizes,
                binsize: this.selectedBinsize,
                widgetData: this.widgetData,
                isICCF: this.isICCF,
                widgetType: "Hi-C"
            }
        },
        deleteWidget: function(){
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id
            }
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
        },
        handleDragStart: function(e) {
            // commit to store once drag starts
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            // create data transfer object
            e.dataTransfer.setData('widget-id', this.id);
            e.dataTransfer.setData("collection-id", this.collectionID);
        },
        sameCollectionConfig: function(newCollectionData, oldCollectionData) {
            if ( !oldCollectionData ){
                // no old data -> the widget needs to be freshly initialized
                return false;
            }
            if (newCollectionData["intervalID"] != oldCollectionData["intervalID"]){
                return false;
            }
            return true;
        },
        initializeAtNewCollection: function(widgetData, collectionData) {
            return {
                widgetData: undefined,
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalID: collectionData["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: this.$store.getters.getCoolers,
                isICCF: true
            }
        },
        initializeAtSameCollection: function(widgetData, collectionData) {
            return {
                widgetData: widgetData["widgetData"],
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalID: collectionData["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: this.$store.getters.getCoolers,
                isICCF: widgetData["isICCF"]
            }
        },
        initializeWidget: function() {
            // initialize widget from store
            var queryObject = {
                parentID: this.collectionID,
                id: this.id
            };
            var widgetData = this.$store.getters["compare/getWidgetProperties"](queryObject);
            // the collection config at the current collection
            var collectionData = this.$store.getters["compare/getCollectionProperties"](this.collectionID);
            // the collection config the widget comes from
            var oldCollectionData = widgetData["collectionData"];
            if (this.sameCollectionConfig(collectionData, oldCollectionData)){
                return this.initializeAtSameCollection(widgetData, collectionData)
            }
            return this.initializeAtNewCollection(widgetData, collectionData)
        }
    },
    watch: {
        "$store.state.datasets": function() {
            // updates datasets if they change
            this.datasets = this.$store.getters.getCoolers
        },
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue) {
                        // check if intervals has changed
                        var newEntry = newValue[this.collectionID]["intervalID"];
                        if ( newEntry != this.intervalID ){
                            this.intervalID = newEntry;
                            // reset state
                            this.selectedBinsize = undefined,
                            this.selectedDataset = undefined,
                            this.widgetData = undefined,
                            this.binsizes = []
                        }

                     },
        },
        selectedDataset: function() {
            if (!this.selectedDataset){
                // do not dispatch call if there is no id --> can happend when reset
                return
            }
            // fetch binsizes for the current combination of dataset and intervals
            this.fetchData(`averageIntervalData/?cooler_id=${this.selectedDataset}&intervals_id=${this.intervalID}`).then((response) => {
                // update binsizes to show and group iccf/obsExp data under one binsize
                this.binsizes = group_iccf_obs_exp(response.data);
                });
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize){
                return
            }
            // fetch widget data
            var iccf_id = this.binsizes[this.selectedBinsize]["ICCF"];
            var obs_exp_id = this.binsizes[this.selectedBinsize]["Obs/Exp"];
                // get pileup iccf; update pileup data upon success
            var iccfresponse = await this.fetchData(`averageIntervalData/${iccf_id}/`);
            // get pileup obs/exp; update pileup data upon success
            var obsExpresponse = await this.fetchData(`averageIntervalData/${obs_exp_id}/`);
            this.widgetData = {
                "ICCF": JSON.parse(iccfresponse.data),
                "ObsExp": JSON.parse(obsExpresponse.data)
            };
        }
    }
}
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
    padding-top: 2px;
}

.padding-top-large {
    padding-top: 10px;
}

.smallMargin {
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 2px;
    margin-bottom: 1px;
}


</style>