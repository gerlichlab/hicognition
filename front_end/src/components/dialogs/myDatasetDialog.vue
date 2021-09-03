<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Datasets</md-dialog-title>
            <md-content class="content">
                <datasetTable :datasets="datasets"></datasetTable>
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
import { apiMixin } from "../../mixins";

export default {
    name: "MyDatasetDialog",
    mixins: [apiMixin],
    components: {
        datasetTable
    },
    data: function(){
        return {
            datasets: undefined
        }
    },
    props: {
        dialog: Boolean
    },
    methods: {
        fetchDatasets() {
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
    },
    mounted: function() {
        this.fetchDatasets()
    },
    watch: {
        showDialog: function(val){
            if (val){
                this.datasets = undefined
                this.fetchDatasets()
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
