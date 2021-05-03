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
                                v-for="item in datasets"
                                :value="item.id"
                                :key="item.id"
                                >{{ item.dataset_name }}</md-option
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
                                v-for="item in binsizes"
                                :value="item.binsize"
                                :key="item.binsize"
                                >{{
                                    convertBasePairsToReadable(item.binsize)
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
                :width="lineProfileWidth"
                :height="lineProfileHeight"
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
import { apiMixin, formattingMixin } from "../../mixins";
import { group_lineprofils_by_binsize } from "../../functions";
import EventBus from "../../eventBus";

const TOOLBARHEIGHT = 71;

export default {
    name: "lineprofileWidget",
    mixins: [apiMixin, formattingMixin],
    components: {
        lineprofile
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
        lineProfileHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT) * 0.75);
        },
        lineProfileWidth: function() {
            return Math.round(this.width * 0.7);
        },
        showData: function() {
            if (this.widgetData) {
                return true;
            }
            return false;
        },
        allowDatasetSelection: function() {
            if (this.intervalID) {
                return true;
            }
            return false;
        },
        allowBinsizeSelection: function() {
            return this.binsizes.length != 0;
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
        deleteWidget: function() {
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id
            };
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
            // remove old dataset ids from used values in store
            for (let dataset_id_old of this.selectedDataset){
                this.$store.commit("compare/decrement_usage_dataset", dataset_id_old)
            }

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
                newCollectionData["intervalID"] !=
                oldCollectionData["intervalID"]
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
                selectedDataset: [],
                selectedBinsize: undefined,
                intervalID: collectionData["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: this.$store.getters.getBigwigsDirty,
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
        initializeAtNewCollection: function(widgetData, collectionConfig) {
            return {
                widgetDataRef: undefined,
                dragImage: undefined,
                widgetData: undefined,
                selectedDataset: [],
                selectedBinsize: undefined,
                intervalID: collectionConfig["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: this.$store.getters.getBigwigsDirty,
                isDefault: true,
                lineProfileNames: [],
                showMenu: false,
                normalized: false
            };
        },
        initializeAtSameCollection: function(widgetData, collectionConfig) {
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
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                lineProfileNames: widgetData["lineProfileNames"],
                intervalID: collectionConfig["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: this.$store.getters.getBigwigsDirty,
                isDefault: widgetData["isDefault"],
                showMenu: false,
                normalized: widgetData["normalized"]
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
        getlineprofileName: async function(id) {
            // fetch it
            var response = await this.fetchData(`datasets/${id}/name/`);
            var parsed = response.data;
            // return it
            return parsed;
        }
    },
    watch: {
        "$store.state.datasets": function() {
            // updates datasets if they change -> get coolers that may be in the status of processing
            this.datasets = this.$store.getters.getBigwigsDirty;
        },
        // watch for changes in store to be able to update intervals
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue) {
                // check if collecitonConfig is defined
                if ("collectionConfig" in newValue[this.collectionID]) {
                    // check if intervals has changed
                    var newEntry =
                        newValue[this.collectionID]["collectionConfig"][
                            "intervalID"
                        ];
                    if (newEntry != this.intervalID) {
                        this.intervalID = newEntry;
                        // reset state
                        this.selectedBinsize = undefined;
                        this.selectedDataset = undefined;
                        this.widgetData = undefined;
                        this.binsizes = [];
                    }
                }
            }
        },
        selectedDataset: async function(newVal, oldVal) {
            if (
                this.selectedDataset == undefined ||
                this.selectedDataset.length == 0
            ) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // fetch binsizes for the current combination of dataset and intervals
            await this.fetchData(
                `averageIntervalData/?dataset_id=${this.selectedDataset}&intervals_id=${this.intervalID}`
            ).then(response => {
                this.binsizes = group_lineprofils_by_binsize(response.data);
                //this.binsizes = response.data;
            });
            // remove old dataset ids from used values in store
            for (let dataset_id_old of oldVal){
                this.$store.commit("compare/decrement_usage_dataset", dataset_id_old)
            }
            // add new datasets to used values in store
            for (let dataset_id_new of newVal){
                this.$store.commit("compare/increment_usage_dataset", dataset_id_new)
            }
            // if no binsizes selected, return 
            if (!this.selectedBinsize) {
                return;
            }
            var selected_ids;
            for (let [key, entry] of Object.entries(this.binsizes)) {
                if (this.selectedBinsize == key) {
                    selected_ids = entry.id;
                }
            }

            // store widget data ref

            this.widgetDataRef = selected_ids;

            var selected_data = [];
            for (let selected_id of selected_ids) {
                selected_data.push(await this.getlineprofileData(selected_id));
            }
            //this.widgetData = selected_data;
            var selected_names = [];
            for (let selected_id of this.selectedDataset) {
                selected_names.push(await this.getlineprofileName(selected_id));
            }
            this.lineProfileNames = selected_names;
            this.widgetData = selected_data;
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            // fetch widget data
            var selected_ids;
            // add list of names
            for (let [key, entry] of Object.entries(this.binsizes)) {
                if (this.selectedBinsize == key) {
                    //.id is an array
                    selected_ids = entry.id;
                }
            }

            // store widget data ref
            this.widgetDataRef = selected_ids;

            var selected_data = [];
            for (let selected_id of selected_ids) {
                selected_data.push(await this.getlineprofileData(selected_id));
            }
            // add list of names
            var selected_names = [];
            for (let selected_id of this.selectedDataset) {
                selected_names.push(await this.getlineprofileName(selected_id));
            }
            this.lineProfileNames = selected_names;
            this.widgetData = selected_data;
        }
    },
    mounted: function (){
        EventBus.$on('serialize-widgets', this.serializeWidget)
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
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 2px;
    margin-bottom: 1px;
}

.md-field {
    min-height: 30px;
}
</style>
