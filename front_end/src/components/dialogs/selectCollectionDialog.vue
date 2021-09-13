<template>
    <div style="z-index: 500;">
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>{{ this.title }}</md-dialog-title>
            <md-content class="content">
                <collectionTable
                    :collections="collections"
                    :restrictedDatasetType="datasetType"
                    :singleSelection="singleSelection"
                    :showEmpty="showEmpty"
                    :preselection="preselection"
                    :assembly="assembly"
                    :finishedCollections="finishedCollections"
                    :processingCollections="processingCollections"
                    :failedCollections="failedCollections"
                    @selection-changed="handleSelectionChange"
                ></collectionTable>
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
import collectionTable from "../tables/collectionTable";

import EventBus from "../../eventBus";

export default {
    name: "selectCollectionDialog",
    components: {
        collectionTable
    },
    data: function() {
        return {
            selection: []
        };
    },
    props: {
        dialog: Boolean,
        collections: Array,
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
        finishedCollections: {
            type: Array,
            default: undefined
        },
        processingCollections: {
            type: Array,
            default: undefined
        },
        failedCollections: {
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
                EventBus.$emit("collection-selected", this.selection[0]);
            } else {
                EventBus.$emit("collection-selected", this.selection);
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
                return "Collections";
            }
            return "Available Collections";
        },
        showEmpty: function() {
            if (!this.collections) {
                return undefined;
            }
            return this.collections.length == 0;
        },
        showControls: function() {
            return this.selection.length !== 0;
        },
        showDialog: function() {
            return this.dialog;
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
