<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Datasets</md-dialog-title>
            <md-content class="content">
                <datasetTable
                    :datasets="datasets"
                    :restrictedDatasetType="datasetType"
                    :singleSelection="true"
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
    },
    methods: {
        handleSelectionChange: function (selection) {
            this.selection = selection;
        },
        handleSelect: function () {
            EventBus.$emit('dataset-selected', this.selection[0])
            this.$emit('close-dialog')
        },
        handleClose: function(){
            this.$emit('close-dialog');
            EventBus.$emit('selection-aborted')
            this.selection = []
        }
    },
    computed: {
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


@media only screen and (min-width: 1800px) {

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
}


.content {
    margin: 10px;
    flex: 1 1;
}
</style>
