<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Datasets</md-dialog-title>
            <md-content class="content">
                <datasetTable></datasetTable>
            </md-content>
            <md-dialog-actions>
                <md-button class="md-primary" @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>

<script>
import datasetTable from "../tables/datasetTable";

export default {
    name: "MyDatasetDialog",
    components: {
        datasetTable
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        }
    },
    watch: {
        showDialog: function(val) {
            if (val) {
                // switched on
                this.$emit("get-datasets");
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 90vw;
    min-width: 60vw;
    min-height: 50vh;
}

.content {
    margin: 10px;
    flex: 1 1;
}
</style>
