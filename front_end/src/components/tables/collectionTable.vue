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
            <md-table-toolbar >
                <!-- Update button -->
                <div >
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
            </md-table-row>
        </md-table>
        <md-snackbar :md-active.sync="datasetsDeleted"
            >Deletion done!</md-snackbar
        >
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";

export default {
    name: "collectionTable",
    mixins: [apiMixin],
    data: () => ({
        selected: undefined,
        collections: [],
        clickedDelete: false,
        datasetsDeleted: false
    }),
    methods: {
        deleteClicked: function() {
            this.clickedDelete = true;
        },
        handleDelete: async function() {
            return
        },
        onSelect(item) {
            this.selected = item;
        },
        fetchSessions() {
            this.fetchData("collections/").then(response => {
                if (response) {
                    // update displayed datasets
                    this.sessions = response.data;
                }
            });
        }
    },
    watch: {
        selected: function(val){
            if (val != undefined){
                this.$emit("selection-available", this.selected.id)
            }else{
                this.$emit("selection-unavailable")
            }
        }
    },
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