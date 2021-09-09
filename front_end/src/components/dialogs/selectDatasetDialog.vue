<template>
    <div style="z-index: 500;">
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Datasets</md-dialog-title>
            <md-content class="content">
                <datasetTable
                    :datasets="datasets"
                    :restrictedDatasetType="datasetType"
                    :singleSelection="singleSelection"
                    :showEmpty="showEmpty"
                    :preselection="preselection"
                    :assembly="assembly"
                    :finishedDatasets="finishedDatasets"
                    @selection-changed="handleSelectionChange"
                ></datasetTable>
            </md-content>
            <md-dialog-actions>

                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="handleSelect"
                            v-if="showControls"
                            >Select</md-button
                        >
                    </div>
                    <div class="float-right">
                        <md-button
                            class="md-secondary"
                            @click="handleClose"
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
        datasetTable,
    },
    data: function () {
        return {
            selection: [],
        };
    },
    props: {
        dialog: Boolean,
        datasets: Array,
        datasetType: String,
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
        }
    },
    methods: {
        handleSelectionChange: function (selection) {
            this.selection = selection;
        },
        handleSelect: function () {
            if (this.singleSelection){
                EventBus.$emit('dataset-selected', this.selection[0])
            } else {
                EventBus.$emit('dataset-selected', this.selection)
            }
            this.$emit('close-dialog')
        },
        handleClose: function(){
            this.$emit('close-dialog');
            EventBus.$emit('selection-aborted')
            this.selection = []
        }
    },
    computed: {
        showEmpty: function(){
            if (!this.datasets){
                return undefined
            }
            return this.datasets.length == 0
        },
        showControls: function () {
            return this.selection.length !== 0;
        },
        showDialog: function () {
            return this.dialog;
        },
    },
};
</script>

<style lang="scss" scoped>

    .md-dialog /deep/.md-dialog-container {
        max-width: 90vw;
        min-width: 90vw;
        min-height: 90vh;
    }


@media only screen and (min-width: 2400px) {

    .md-dialog /deep/.md-dialog-container {
        max-width: 90vw;
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
    margin: 5px
}


.content {
    margin: 10px;
    flex: 1 1;
}
</style>
