<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Datasets</md-dialog-title>
            <md-content class="content">
                <datasetTable
                    :datasets="datasets"
                    :restrictedDatasetType="datasetType"
                    @load-datasets="this.fetchDatasets"
                    @selection-changed="handleSelectionChange"
                ></datasetTable>
            </md-content>
            <md-dialog-actions>

                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="showDelete = true"
                            v-if="showControls && !showDelete"
                            :disabled="!notProcessing"
                            >Delete
                            </md-button
                        >
                        <md-tooltip md-direction="top" v-if="!notProcessing">Datasets cannot be delete when one of them is processing</md-tooltip>
                    </div>
                    <div class="float-left">
                        <md-button
                            class="md-raised"
                            v-if="showDelete"
                            >Are you sure?</md-button
                        >
                    </div>
                    <div class="float-left">
                        <md-button
                            class="md-raised md-accent"
                            @click="handleDelete"
                            v-if="showDelete"
                            >Yes</md-button
                        >
                    </div>
                    <div class="float-left">
                        <md-button
                            class="md-raised md-primary"
                            @click="showDelete = false"
                            v-if="showDelete"
                            >No</md-button
                        >
                    </div>
                    <div class="float-left">
                        <md-button
                            class="md-primary"
                            @click="handleEditClick"
                            v-if="showControls && !showDelete && singleDatasetSelected"
                            >Edit</md-button
                        >
                    </div>
                    <div class="float-right">
                        <md-button
                            class="md-secondary"
                            @click="
                                $emit('close-dialog');
                                selection = []
                            "
                            >Close</md-button
                        >
                    </div>
                </div>
            </md-dialog-actions>
        </md-dialog>
        <md-snackbar :md-active.sync="datasetsDeleted"
            >Deletion done!</md-snackbar
        >
    </div>
</template>

<script>
import datasetTable from "../tables/datasetTable";
import { apiMixin } from "../../mixins";

import EventBus from "../../eventBus"

export default {
    name: "MyDatasetDialog",
    mixins: [apiMixin],
    components: {
        datasetTable,
    },
    data: function () {
        return {
            datasets: [],
            showDelete: false,
            clickedDelete: false,
            datasetsDeleted: false,
            selection: [],
        };
    },
    props: {
        dialog: Boolean,
        datasetType: {
            type: String,
            default: "bedfile"
        }
    },
    methods: {
        handleSelectionChange: function (selection) {
            this.selection = selection;
        },
        handleEditClick: function(){
            EventBus.$emit("show-modify-dialog", this.selection[0])
        },
        handleDelete: async function() {
            this.showDelete = false;
            for (let id of this.selection) {
                await this.deleteData(`datasets/${id}/`);
            }
            this.datasetsDeleted = true;
            this.selection = [];
            this.fetchDatasets();
        },
        getDatasets: function () {
            this.datasets = this.$store.state.datasets
        },
        fetchDatasets: function() {
            this.datasets = [];
            this.fetchData("datasets/").then((response) => {
                if (response) {
                    // success, store datasets
                    this.$store.commit("setDatasets", response.data);
                    // update displayed datasets
                    setTimeout(() => {
                        this.datasets = response.data;
                    }, 100);
                }
            });
        },
    },
    computed: {
        notProcessing: function(){
            return this.datasets.every(el => el.processing_datasets.length === 0)
        },
        singleDatasetSelected: function(){
            return this.selection.length === 1;
        },
        showControls: function () {
            return this.selection.length !== 0;
        },
        showDialog: function () {
            return this.dialog;
        },
    },
    watch: {
        showDialog: function (val) {
            if (val) {
                // switched on
                this.$emit("get-datasets");
            }
        },
    },
    watch: {
        showDialog: function (val) {
            if (val) {
                this.getDatasets();
            }
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
    margin: 5px;
}


.content {
    margin: 10px;
    flex: 1 1;
}
</style>
