<template>
    <div>
        <md-table
            v-model="collections"
            md-sort="name"
            md-sort-order="asc"
            md-card
            md-fixed-header
            @md-selected="onSelect"
        >
            <!-- Table toolbar has the update button and the search field -->
            <md-table-toolbar>
                <!-- Update button -->
                <div>
                    <div>
                        <md-button
                            class="md-dense md-raised button-margin md-primary md-icon-button"
                            @click="fetchCollections"
                        >
                            <md-icon>cached</md-icon>
                        </md-button>
                    </div>
                </div>
            </md-table-toolbar>

            <!-- Empty state for table -->
            <md-table-empty-state
                md-label="No collections found"
                :md-description="
                    `No collections found. Go to add collection to create a new session.`
                "
            >
            </md-table-empty-state>
            <!-- Definition of how table should look -->
            <md-table-row
                slot="md-table-row"
                slot-scope="{ item }"
                md-selectable="single"
                class="md-primary"
                md-auto-select
            >
                <md-table-cell md-label="Name" md-sort-by="name">{{
                    item.name
                }}</md-table-cell>
                <md-table-cell md-label="Type" md-sort-by="kind">{{
                    item.kind
                }}</md-table-cell>
                <md-table-cell
                    md-label="Number Datasets"
                    md-sort-by="number_datasets"
                    >{{ item.number_datasets }}</md-table-cell
                >
                <md-table-cell md-label="">

                    <md-list >
                        <!-- stop prevent is needed for table to not change styles based on click event -->
                        <md-list-item md-expand @click.stop.prevent>
                            <span class="md-list-item-text" :style="containedDatasetStyle">Contained Datasets</span>
                        <md-list slot="md-expand">
                            <md-list-item v-for="name in item.dataset_names" :key="name">{{name}}</md-list-item>
                        </md-list>
                        </md-list-item>
                    </md-list>

                </md-table-cell>
                <md-table-cell
                    md-label="Progress"
                    md-sort-by="processing_state"
                >
                    <md-icon v-if="item.processing_state == 'finished'"
                        >done</md-icon
                    >
                    <md-progress-spinner
                        :md-diameter="30"
                        md-mode="indeterminate"
                        v-else-if="item.processing_state == 'processing'"
                    ></md-progress-spinner>
                    <md-icon v-else-if="item.processing_state == 'failed'"
                        >error</md-icon
                    >
                    <md-icon v-else-if="item.processing_state == 'uploaded'"
                        >cloud_done</md-icon
                    >
                    <md-icon v-else-if="item.processing_state == 'uploading'"
                        >cloud_upload</md-icon
                    >
                </md-table-cell>
            </md-table-row>
        </md-table>
        <md-snackbar :md-active.sync="datasetsDeleted"
            >Deletion done!</md-snackbar
        >
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";
import EventBus from "../../eventBus";

export default {
    name: "collectionTable",
    mixins: [apiMixin],
    data: () => ({
        selected: undefined,
        collections: [],
        clickedDelete: false,
        datasetsDeleted: false
    }),
    computed: {
        containedDatasetStyle: function(){
            if (this.selected){
                return {
                    "color": "black"
                }
            }
            return
        }
    },
    methods: {
        deleteClicked: function() {
            this.clickedDelete = true;
        },
        handleDelete: async function() {
            return;
        },
        onSelect(item) {
            this.selected = item;
        },
        fetchCollections() {
            this.fetchData("collections/").then(response => {
                if (response) {
                    // update displayed datasets
                    this.collections = response.data;
                }
            });
        }
    },
    watch: {
        selected: function(val) {
            if (val != undefined) {
                this.$emit("selection-available", this.selected.id);
            } else {
                this.$emit("selection-unavailable");
            }
        }
    },
    created: function() {
        EventBus.$on("fetch-sessions", this.fetchCollections);
        this.fetchCollections();
    },
    beforeDestroy: function() {
        EventBus.$off("fetch-sessions", this.fetchCollections);
    }
};
</script>

<style lang="scss" scoped>
.md-field {
    max-width: 200px;
}
.md-table {
    max-width: 90vw;
    min-width: 40vw;
}
.md-table-cell {
    text-align: center;
}

</style>
