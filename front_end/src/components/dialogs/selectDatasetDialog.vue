<template>
    <div style="z-index: 500">
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>{{ this.title }}</md-dialog-title>
            <md-content class="content">
                <datasetTable
                    :datasets="datasets"
                    :restrictedDatasetType="showedDatasetType"
                    :block2d="block2d"
                    :singleSelection="singleSelection"
                    :showEmpty="showEmpty"
                    :preselection="preselection"
                    :assembly="assembly"
                    :finishedDatasets="finishedDatasets"
                    :processingDatasets="processingDatasets"
                    :failedDatasets="failedDatasets"
                    :blockProcessingDialog="true"
                    @selection-changed="handleSelectionChange"
                ></datasetTable>
            </md-content>
            <md-dialog-actions>
                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="handleSelect"
                            v-if="showControls && reactToSelection"
                            >Select</md-button
                        >
                    </div>
                    <div class="float-right">
                        <md-button class="md-secondary" @click="handleClose"
                            >Close</md-button
                        >
                    </div>
                </div>
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>

<script>
import datasetTable from "../tables/datasetTable";

import EventBus from "../../eventBus";

export default {
    name: "selectDatasetDialog",
    components: {
        datasetTable
    },
    data: function() {
        return {
            selection: []
        };
    },
    props: {
        dialog: Boolean,
        datasets: Array,
        datasetType: String,
        reactToSelection: {
            type: Boolean,
            default: true
        },
        singleSelection: {
            type: Boolean,
            default: true
        },
        preselection: Array,
        assembly: {
            type: Number,
            default: undefined
        },
        finishedDatasets: {
            type: Array,
            default: undefined
        },
        processingDatasets: {
            type: Array,
            default: undefined
        },
        failedDatasets: {
            type: Array,
            default: undefined
        }
    },
    methods: {
        handleSelectionChange: function(selection) {
            this.selection = selection;
        },
        handleSelect: function() {
            if (this.singleSelection) {
                EventBus.$emit("dataset-selected", this.selection[0]);
            } else {
                EventBus.$emit("dataset-selected", this.selection);
            }
            this.$emit("close-dialog");
        },
        handleClose: function() {
            this.$emit("close-dialog");
            EventBus.$emit("selection-aborted");
            this.selection = [];
        }
    },
    computed: {
        title: function() {
            if (this.reactToSelection) {
                return "Datasets";
            }
            return "Available Features";
        },
        showEmpty: function() {
            if (!this.datasets) {
                return undefined;
            }
            return this.datasets.length == 0;
        },
        showControls: function() {
            return this.selection.length !== 0;
        },
        showDialog: function() {
            return this.dialog;
        },
        block2d: function(){
            if (this.datasetType == 'bedfile-1d'){
                return true
            }
            return false
        },
        showedDatasetType: function(){
            if (this.datasetType == 'bedfile-1d'){
                return 'bedfile'
            }else{
                return this.datasetType
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 70vw;
    min-width: 70vw;
    min-height: 70vh;
}

@media only screen and (min-width: 2400px) {
    .md-dialog /deep/.md-dialog-container {
        max-width: 60vw;
        min-width: 50vw;
        min-height: 50vh;
    }
}

.full-width {
    width: 100%;
}

.float-left {
    float: left;
    margin: 5px;
}

.float-right {
    float: right;
    margin: 5px;
}

.content {
    margin: 10px;
    flex: 1 1;
}
</style>
