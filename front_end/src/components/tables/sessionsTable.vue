<template>
    <div>
        <md-table
            v-model="sessions"
            md-sort="session_name"
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
                            @click="fetchSessions"
                        >
                            <md-icon>cached</md-icon>
                        </md-button>
                    </div>
                </div>
            </md-table-toolbar>

            <!-- Empty state for table -->
            <md-table-empty-state
                md-label="No sessions found"
                :md-description="
                    `No sessions found for this query. Try a different search term or create a new session.`
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
                <md-table-cell md-label="Created" md-sort-by="created">{{
                    item.created
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
        sessions: [],
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
        getAlternateLabel(count) {
            let plural = "";

            if (count > 1) {
                plural = "s";
            }

            return `${count} data set${plural} selected`;
        },
        onSelect(item) {
            this.selected = item;
        },
        fetchSessions() {
            this.fetchData("sessions/").then(response => {
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
                this.$emit("selection-available", this.selected.session_object, this.selected.id)
            }else{
                this.$emit("selection-unavailable")
            }
        }
    },
    created: function() {
        EventBus.$on("fetch-sessions", this.fetchSessions)
        this.fetchSessions()
    },
    beforeDestroy: function(){
        EventBus.$off("fetch-sessions")
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
