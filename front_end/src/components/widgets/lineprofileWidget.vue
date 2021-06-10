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
                    class="md-layout-item md-size-35 padding-left padding-right"
                >
                    <md-field class="padding-top">
                        <label class="md-primary">Dataset</label>
                        <md-select
                            v-model="selectedDataset"
                            name="dataset"
                            id="dataset"
                            placeholder="Dataset"
                            multiple
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
                                <md-list-item class="md-inset" @click="normalized = false; showMenu=false" >
                                     <span class="md-body-1">Unscaled</span>
                                     <md-icon
                                            v-if="!normalized"
                                            >done</md-icon
                                    >
                                </md-list-item>
                                <md-list-item class="md-inset" @click="normalized = true; showMenu=false">
                                    <span class="md-body-1">Normalized</span>
                                    <md-icon
                                            v-if="normalized"
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
            <lineprofile
                v-if="showData"
                :lineprofileID="id"
                :width="visualizationWidth"
                :height="visualizationHeight"
                :lineprofileNames="lineProfileNames"
                :lineprofileData="widgetData"
                :normalized="normalized"
                :log="true"
            >
            </lineprofile>
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
import lineprofile from "../visualizations/lineprofile";
import { apiMixin, formattingMixin, widgetMixin } from "../../mixins";
import EventBus from "../../eventBus";


export default {
    name: "lineprofileWidget",
    mixins: [apiMixin, formattingMixin, widgetMixin],
    components: {
        lineprofile
    },
    computed: {
    },
    methods: {
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
                widgetType: "Lineprofile",
                normalized: this.normalized
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
                emptyClass: ["smallMargin", "empty"],
                binsizes: {},
                datasets: collectionData["availableData"]["lineprofile"],
                isDefault: true,
                lineProfileNames: [],
                showMenu: false,
                normalized: false
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
                var widgetDataValues = [];
                for (var widget_data_id of widgetDataRef) {
                    // deinfe store queries
                    var payload = {
                        id: widget_data_id
                    };
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
            if (widgetData["dataset"]){
                for (let datasetId of widgetData["dataset"]){
                    this.$store.commit("compare/increment_usage_dataset", datasetId)
                }
            }
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                lineProfileNames: widgetData["lineProfileNames"],
                intervalSize: collectionConfig["intervalSize"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: collectionConfig["availableData"]["lineprofile"],
                isDefault: widgetData["isDefault"],
                showMenu: false,
                normalized: widgetData["normalized"]
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
        updateData: async function(){
            // construct data ids to be fecthed
            let selected_ids = this.binsizes[this.selectedBinsize]
            // store widget data ref
            this.widgetDataRef = selected_ids;
            // fetch data
            var selected_data = [];
            for (let selected_id of selected_ids) {
                selected_data.push(await this.getlineprofileData(selected_id));
            }
            // get lineprofile names
            this.lineProfileNames = this.selectedDataset.map(elem => {
                return this.datasets[elem]["name"]
            })
            this.widgetData = selected_data;
        },
        getIdsOfBinsizes: function(){
            // takes selected dataset array and constructs an object with binsizes and arrays of data ids
            let binsizes ={};
            for (let selectedDataset of this.selectedDataset){
                let temp_binsizes = this.datasets[selectedDataset]["data_ids"][this.intervalSize];
                for (let [key, value] of Object.entries(temp_binsizes)){
                    if (!(key in binsizes)){
                        binsizes[key] = [value]
                    }else{
                        binsizes[key].push(value)
                    }
                }
            }
            return binsizes
        }
    },
    watch: {
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue) {
                // update availability object
                this.datasets = newValue[this.collectionID]["collectionConfig"]["availableData"]["lineprofile"]
                this.intervalSize = newValue[this.collectionID]["collectionConfig"]["intervalSize"]
            }
        },
        datasets: function(newVal, oldVal){
            if (!newVal || !oldVal || !this.selectedDataset || (this.selectedDataset.length == 0)){
                return
            }
            this.binsizes = this.getIdsOfBinsizes()
            this.selectedBinsize = this.getCenterOfArray(Object.keys(this.binsizes))
            this.updateData()
        },
        intervalSize: function(newVal, oldVal){
            // if interval size changes, reload data
            if (!newVal || !oldVal || (this.selectedDataset.length == 0)){
                return
            }
            this.binsizes = this.getIdsOfBinsizes()
            this.selectedBinsize = this.getCenterOfArray(Object.keys(this.binsizes))
            this.updateData()
        },
        selectedDataset: async function(newVal, oldVal) {
            if (
                this.selectedDataset.length == 0
            ) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // set binsizes -> there can be multiple datasets, binsizes need to be collected for them
            this.binsizes = this.getIdsOfBinsizes()
            // remove old dataset ids from used values in store
            for (let dataset_id_old of oldVal){
                this.$store.commit("compare/decrement_usage_dataset", dataset_id_old)
            }
            // add new datasets to used values in store
            for (let dataset_id_new of newVal){
                this.$store.commit("compare/increment_usage_dataset", dataset_id_new)
            }
            // if no binsizes selected, set default and return
            if (!this.selectedBinsize) {
                this.selectedBinsize = this.getCenterOfArray(Object.keys(this.binsizes))
            }else{
                this.updateData()
            }
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            this.updateData()
        }
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
    margin: 2px
}

.md-field {
    min-height: 30px;
}
</style>
