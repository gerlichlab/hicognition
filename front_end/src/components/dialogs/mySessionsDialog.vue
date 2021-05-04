<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Available Sessions</md-dialog-title>
            <md-content class="content">
                <sessionsTable
                    @selection-available="handleSelectionAvailable"
                    @selection-unavailable="handleSelectionUnAvailable"
                ></sessionsTable>
            </md-content>
            <div class="md-layout md-gutter md-alignment-center-center no-margin" v-if="showShareableUrl">
                <div class="md-layout-item md-elevation-1 large-margin">
                    <span class="md-caption center-span large-margin">{{ shareableUrl }}</span>
                </div>
            </div>
            <md-dialog-actions>
                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="handleSessionDeletion"
                            v-if="showRestore"
                            >Delete</md-button
                        >
                    </div>
                    <div class="float-right">
                        <md-button
                            class="md-primary"
                            @click="handleUrlgeneration"
                            v-if="showRestore"
                            >Get URL</md-button
                        >
                    </div>
                    <div class="float-right">
                        <md-button
                            class="md-primary"
                            @click="handleSessionRestoration"
                            v-if="showRestore"
                            >Restore</md-button
                        >
                    </div>
                    <div class="float-right">
                        <md-button
                            class="md-secondary"
                            @click="
                                $emit('close-dialog');
                                showRestore = false;
                                selected_session_object = null;
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
import sessionsTable from "../tables/sessionsTable";
import { apiMixin } from "../../mixins";
import EventBus from "../../eventBus";

export default {
    name: "MySessionsDialog",
    mixins: [apiMixin],
    data: function() {
        return {
            showRestore: false,
            selected_session_object: null,
            selected_session_id: null,
            shareableUrl: null
        };
    },
    components: {
        sessionsTable
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        },
        showShareableUrl: function(){
            if (this.selected_session_object && this.shareableUrl){
                return true
            }
            return false
        }
    },
    watch: {
        selected_session_object: function(newVal, oldVal){
            if (newVal != oldVal){
                // blank url
                this.shareableUrl = null
            }
        }
    },
    methods: {
        handleSessionDeletion: function() {
            this.deleteData(`sessions/${this.selected_session_id}/`).then(
                response => {
                    EventBus.$emit("fetch-sessions");
                }
            );
        },
        handleUrlgeneration: function() {
            this.fetchData(
                `sessions/${this.selected_session_id}/sessionToken/`
            ).then(response => {
                let sessionToken = response.data["session_token"];
                var shareableUrl =
                    window.location.host +
                    `/#/main/session?sessionToken=${sessionToken}&sessionID=${this.selected_session_id}`;
                this.shareableUrl = shareableUrl
            });
        },
        handleSessionRestoration: async function() {
            // fetch data references to put into store
            var parsed_object = JSON.parse(this.selected_session_object);
            for (let collection of Object.values(parsed_object)) {
                for (let child of Object.values(collection)) {
                    for (let child_vals of Object.values(child)) {
                        if (child_vals.widgetDataRef) {
                            var widgetType = child_vals.widgetType;
                            switch (widgetType) {
                                case "Lineprofile":
                                    await this.fetchLineProfileData(
                                        child_vals.widgetDataRef
                                    );
                                    break;
                                case "Pileup":
                                    await this.fetchPileupData(
                                        child_vals.widgetDataRef
                                    );
                                    break;
                                case "Stackup":
                                    await this.fetchStackupData(
                                        child_vals.widgetDataRef
                                    );
                            }
                        }
                    }
                }
            }
            this.$store.commit(
                "compare/setWidgetCollections",
                JSON.parse(this.selected_session_object)
            );
            this.selected_session_object = null;
            this.showRestore = false;
            this.shareableUrl = null;
            this.$emit("close-dialog");
        },
        handleSelectionAvailable: function(session_object, session_id) {
            (this.showRestore = true),
                (this.selected_session_object = session_object),
                (this.selected_session_id = session_id);
        },
        fetchLineProfileData: async function(ids) {
            for (let id of ids) {
                // checks whether lineprofile data is in store and does not fetch it if it is there
                if (this.$store.getters["compare/lineprofileExists"](id)) {
                    continue;
                }
                var response = await this.fetchData(
                    `averageIntervalData/${id}/`
                );
                var parsed = response.data;
                // save it in store
                var mutationObject = {
                    id: id,
                    data: parsed
                };
                this.$store.commit(
                    "compare/setWidgetDataLineprofile",
                    mutationObject
                );
            }
        },
        fetchStackupData: async function(id) {
            // checks whether pileup data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (this.$store.getters["compare/stackupExists"](queryObject)) {
                return;
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(
                `individualIntervalData/${id}/`
            );
            var piling_data = response.data;
            // save it in store
            var mutationObject = {
                id: id,
                data: piling_data
            };
            this.$store.commit("compare/setWidgetDataStackup", mutationObject);
        },
        fetchPileupData: async function(dataRef) {
            for (let [pileupType, id] of Object.entries(dataRef)) {
                // checks whether pileup data is in store and fetches it if it is not
                var queryObject = {
                    pileupType: pileupType,
                    id: id
                };
                if (this.$store.getters["compare/pileupExists"](queryObject)) {
                    return;
                }
                // pileup does not exists in store, fetch it
                var response = await this.fetchData(
                    `averageIntervalData/${id}/`
                );
                var parsed = response.data;
                // save it in store
                var mutationObject = {
                    pileupType: pileupType,
                    id: id,
                    data: parsed
                };
                this.$store.commit(
                    "compare/setWidgetDataPileup",
                    mutationObject
                );
            }
        },
        handleSelectionUnAvailable: function() {
            (this.showRestore = false), (this.selected_session_object = null);
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 80vw;
}

.center-span {
    display: table;
    margin: 0 auto;
}

.no-margin {
    margin: 0px;
}

.large-margin {
    margin: 10px;
}

.full-width {
    width: 100%;
}

.float-left {
    float: left;
}

.float-right {
    float: right;
}

.content {
    margin: 10px;
}
</style>
