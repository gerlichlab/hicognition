<template>
    <div>
        <md-table
            v-model="assemblies"
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
                            @click="fetchAssemblies"
                        >
                            <md-icon>cached</md-icon>
                        </md-button>
                    </div>
                </div>
            </md-table-toolbar>

            <!-- Empty state for table -->
            <md-table-empty-state
                md-label="No assemblies found"
                :md-description="
                    `No sessions assemblies found.`
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
                :md-disabled="isSelectionDisabled(item)"
            >
                <md-table-cell md-label="Organism" md-sort-by="organism">{{
                    item.organism
                }}</md-table-cell>
                <md-table-cell md-label="name" md-sort-by="name">{{
                    item.name
                }}</md-table-cell>
                <md-table-cell md-label="Dependent datasets" md-sort-by="dependent_datasets">{{
                    item.dependent_datasets
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
import EventBus from "../../eventBus"

export default {
    name: "sessionTable",
    mixins: [apiMixin],
    data: () => ({
        selected: undefined,
        assemblies: [],
        clickedDelete: false,
        datasetsDeleted: false
    }),
    methods: {
        isSelectionDisabled: function(item) {
            // check if assembly is owned
            var user_id = this.$store.getters.getUserId;
            if (user_id != item.user_id) {
                return true;
            }
            if (item.dependent_dastasets != "0"){
                return true
            }
            return false;
        },
        deleteClicked: function() {
            this.clickedDelete = true;
        },
        onSelect(item) {
            this.selected = item;
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then(response => {
                if (response) {
                    // update displayed assemblies
                    let assemblies = []
                    for (let org of Object.keys(response.data)){
                        for (let assembly of response.data[org]){
                            assembly["organism"] = org
                            assemblies.push(assembly)
                        }
                    }
                    this.assemblies = assemblies;
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
    created: function() {
        EventBus.$on("fetch-assemblies", this.fetchAssemblies)
        this.fetchAssemblies()
    },
    beforeDestroy: function(){
        EventBus.$off("fetch-assemblies")
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
