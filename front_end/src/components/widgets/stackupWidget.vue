<template>
    <div>
        <div
            :style="cssStyle"
            class="smallMargin md-elevation-1 bg"
            draggable="true"
            @dragstart="handleDragStart"
            @dragend="handleDragEnd"
        >
            <div class="md-layout">
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
                                v-for="item in datasets"
                                :value="item.id"
                                :key="item.id"
                                >{{ item.dataset_name }}</md-option
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
            <stackup
                v-if="showData"
                :stackupID="id"
                :width="225"
                :height="225"
                :stackupData="widgetData"
                :log="true"
            >
            </stackup>
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
import stackup from "../visualizations/stackup";
import { apiMixin, formattingMixin } from "../../mixins";
import { convert_tidy_to_pixi, group_stackups_by_binsize } from '../../functions';

export default {
    name: "stackupWidget",
    mixins: [apiMixin, formattingMixin],
    components: {
        stackup
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
                widgetType: "Stackup"
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
                selectedDataset: undefined,
                selectedBinsize: undefined,
                intervalID: collectionData["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: this.$store.getters.getBigwigsDirty,
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
                intervalID: collectionConfig["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: [],
                datasets: this.$store.getters.getBigwigsDirty,
            };
        },
        initializeAtSameCollection: function(widgetData, collectionConfig) {
            var widgetDataValues;
            if (widgetData["widgetDataRef"]) {
                // check if widgetDataRef is defined -> if so, widgetdata is in store
                var widgetDataRef = widgetData["widgetDataRef"];
                // deinfe store queries
                var querydata = {
                    id: widgetDataRef
                };
                // get widget data from store
                widgetDataValues = this.$store.getters["compare/getWidgetDataStackup"](querydata);
            } else {
                widgetDataValues = undefined;
            }
            return {
                widgetDataRef: widgetData["widgetDataRef"],
                dragImage: undefined,
                widgetData: widgetDataValues,
                selectedDataset: widgetData["dataset"],
                selectedBinsize: widgetData["binsize"],
                intervalID: collectionConfig["intervalID"],
                emptyClass: ["smallMargin", "empty"],
                binsizes: widgetData["binsizes"],
                datasets: this.$store.getters.getBigwigsDirty,
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
        getStackupData: async function(id) {
            // checks whether pileup data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (this.$store.getters["compare/stackupExists"](queryObject)) {
                return this.$store.getters["compare/getWidgetDataStackup"](
                    queryObject
                );
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(
                `individualIntervalData/${id}/`
            );
            var piling_data = response.data
            // save it in store
            var mutationObject = {
                id: id,
                data: piling_data
            };
            this.$store.commit("compare/setWidgetDataStackup", mutationObject);
            // return it
            return piling_data;
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
                        this.selectedBinsize = undefined;
                        this.selectedDataset = undefined;
                        this.widgetData = undefined;
                        this.binsizes = [];
                    }
                }
            }
        },
        selectedDataset: function() {
            if (!this.selectedDataset) {
                // do not dispatch call if there is no id --> can happend when reset
                return;
            }
            // fetch binsizes for the current combination of dataset and intervals
            this.fetchData(
                `individualIntervalData/?dataset_id=${this.selectedDataset}&intervals_id=${this.intervalID}`
            ).then(response => {
                // update binsizes to show and group iccf/obsExp data under one binsize
                this.binsizes = group_stackups_by_binsize(response.data);
            });
        },
        selectedBinsize: async function() {
            if (!this.selectedBinsize) {
                return;
            }
            // fetch widget data
            var stackup_id = this.binsizes[this.selectedBinsize]["id"];
            this.widgetDataRef = stackup_id;
            var data = await this.getStackupData(stackup_id);
            this.widgetData = data;
        }
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
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 2px;
    margin-bottom: 1px;
}

.md-field {
    min-height: 30px;
}
</style>
