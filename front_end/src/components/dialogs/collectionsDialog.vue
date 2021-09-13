<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Available Collections</md-dialog-title>
            <md-content class="content">
                <collection-table
                    @selection-available="handleSelectionAvailable"
                    @selection-unavailable="handleSelectionUnAvailable"
                    @load-collections="fetchCollections"
                    :collections="collections"
                ></collection-table>
            </md-content>
            <md-dialog-actions>
                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="handleSessionDeletion"
                            v-if="showDelete"
                            >Delete</md-button
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
            selected_collection_id: null,
            showDelete: false,
            collections: []
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
    },
    methods: {
        fetchCollections() {
            this.fetchData("collections/").then(response => {
                if (response) {
                    // update displayed datasets
                    this.collections = response.data;
                }
            });
        },
        handleSessionDeletion: function() {
            this.deleteData(`collections/${this.selected_collection_id}/`).then(
                response => {
                    EventBus.$emit("fetch-sessions");
                }
            );
        },
        handleSelectionAvailable: function(collection_id) {
                this.selected_collection_id = collection_id;
                this.showDelete = true
        },
        handleSelectionUnAvailable: function() {
            (this.showDelete = false);
        }
    },
    mounted: function(){
        this.fetchCollections()
    }
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
