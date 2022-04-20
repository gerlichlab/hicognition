<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Available Collections</md-dialog-title>
            <md-content class="content">
                <collection-table
                    @load-collections="fetchCollections"
                    @selection-changed="handleSelectionChange"
                    :singleSelection="true"
                    :collections="collections"
                ></collection-table>
            </md-content>
            <md-dialog-actions>
                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="showDelete = true"
                            v-if="showControls && !showDelete && !isDemo"
                            :disabled="!notProcessing"
                            >Delete
                            </md-button
                        >
                        <md-button
                            class="md-secondary md-raised md-accent"
                            v-if="showControls && !showDelete && isDemo"
                            :disabled="!notProcessing"
                            >Delete <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
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
                    <div class="float-right">
                        <md-button
                            class="md-secondary"
                            @click="
                                $emit('close-dialog');
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
import collectionTable from "../tables/collectionTable";
import { apiMixin } from "../../mixins";
import EventBus from "../../eventBus";

export default {
    name: "collectionsDialog",
    mixins: [apiMixin],
    data: function() {
        return {
            showDelete: false,
            collections: [],
            selection: [],
            clickedDelete: false,
            datasetsDeleted: false,
            isDemo: process.env.SHOWCASE
        };
    },
    components: {
        collectionTable
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        },
        showControls: function () {
            return this.selection.length !== 0;
        },
        notProcessing: function(){
            return this.collections.every(el => el.processing_for_regions.length === 0)
        },
    },
    methods: {
        handleSelectionChange: function (selection) {
            this.selection = selection;
        },
        fetchCollections() {
            this.fetchData("collections/").then(response => {
                if (response) {
                    // update displayed datasets
                    this.collections = response.data
                    this.$store.commit("setCollections", response.data)
                }
            });
        },
        handleDelete: function() {
            this.deleteData(`collections/${this.selection[0]}/`).then(
                response => {
                    this.fetchCollections()
                }
            );
        }
    },
    watch: {
        showDialog: function (val) {
            if (val) {
                this.fetchCollections()
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
