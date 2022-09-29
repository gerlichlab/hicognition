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
            <div
                class="md-layout md-gutter md-alignment-center-center no-margin"
                v-if="showShareableUrl"
            >
                <div
                    class="md-layout-item md-elevation-0 large-margin md-size-60"
                >
                    <md-field>
                        <label>Shareable Url</label>
                        <md-input
                            v-model="shareableUrl"
                            readonly
                            ref="urlInput"
                        ></md-input>
                    </md-field>
                </div>
                <div class="md-layout-item md-size-10">
                    <md-button
                        class="md-icon-button md-raised md-primary"
                        @click="copyToClipboard"
                    >
                        <md-icon>content_copy</md-icon>
                    </md-button>
                </div>
            </div>
            <md-dialog-actions>
                <div class="full-width">
                    <div class="float-left">
                        <md-button
                            class="md-secondary md-raised md-accent"
                            @click="handleSessionDeletion"
                            v-if="showRestore && !isDemo"
                            >Delete</md-button
                        >
                        <md-button
                            class="md-secondary md-raised md-accent"
                            v-if="showRestore && isDemo"
                            >Delete
                            <md-tooltip md-direction="top"
                                >Deactivated in demo mode</md-tooltip
                            ></md-button
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
        <md-snackbar
            md-position="center"
            :md-duration="1000"
            :md-active.sync="copySuccesful"
            md-persistent
        >
            <div class="full-width-flexbox-center">
                <span>Copied!</span>
            </div>
        </md-snackbar>
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
            shareableUrl: null,
            copySuccesful: false,
            isDemo: process.env.SHOWCASE
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
        showShareableUrl: function() {
            if (this.selected_session_object && this.shareableUrl) {
                return true;
            }
            return false;
        }
    },
    watch: {
        selected_session_object: function(newVal, oldVal) {
            if (newVal != oldVal) {
                // blank url
                this.shareableUrl = null;
                this.copySuccesful = false;
            }
        }
    },
    methods: {
        copyToClipboard: function() {
            try {
                this.$refs["urlInput"].$el.focus();
                this.$refs["urlInput"].$el.select();
                document.execCommand("copy");
                this.copySuccesful = true;
            } catch (err) {
                console.log("Copying did not work...");
            }
        },
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
                let isDemo = process.env.SHOWCASE;
                if (isDemo) {
                    var shareableUrl =
                        window.location.host +
                        `/app/#/main/session?sessionToken=${sessionToken}&sessionID=${this.selected_session_id}`;
                }
                if (!isDemo) {
                    shareableUrl =
                        window.location.host +
                        `/#/main/session?sessionToken=${sessionToken}&sessionID=${this.selected_session_id}`;
                }

                this.shareableUrl = shareableUrl;
            });
        },
        handleSessionRestoration: async function() {
            // fetch and store session token -> this is needed in case unowned datasets are in session
            let response = await this.fetchData(
                `sessions/${this.selected_session_id}/sessionToken/`
            );
            this.$store.commit(
                "setSessionToken",
                response.data["session_token"]
            );
            // clear widget collections
            this.$store.commit("compare/clearAll");
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
                                    break;
                                case "Lola":
                                    await this.fetchAssociationData(
                                        child_vals.widgetDataRef
                                    );
                                    break;
                                case "Embedding1D":
                                    await this.fetchEmbeddingData(
                                        child_vals.widgetDataRef,
                                        child_vals.overlay
                                    );
                            }
                        }
                    }
                }
            }
            // populate store
            this.$store.commit(
                "compare/setWidgetCollections",
                JSON.parse(this.selected_session_object)
            );
            // event session loaded fro compare route
            EventBus.$emit("session-loaded");
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
        fetchAssociationData: async function(id) {
            // checks whether association data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (
                this.$store.getters["compare/associationDataExists"](
                    queryObject
                )
            ) {
                return;
            }
            // pileup does not exists in store, fetch it
            var response = await this.fetchData(
                `associationIntervalData/${id}/`
            );
            var piling_data = response.data;
            // save it in store
            var mutationObject = {
                id: id,
                data: piling_data
            };
            this.$store.commit("compare/setWidgetDataLola", mutationObject);
        },
        fetchEmbeddingPoints: async function(id) {
            var queryObject = {
                id: id
            };
            if (
                !this.$store.getters["compare/embedding1dDataExists"](
                    queryObject
                )
            ) {
                // points do not exist in store, check whether request for them has been dispatched
                let url = `embeddingIntervalData/${id}/`;
                let requestData = this.$store.getters["compare/getRequest"](
                    url
                );
                let response;
                if (!requestData) {
                    // request has not been dispatched => put it in store
                    this.$store.commit("compare/setRequest", {
                        url: url,
                        data: this.fetchData(url)
                    });
                    response = await this.$store.getters["compare/getRequest"](
                        url
                    );
                    // save it in store
                    var mutationObject = {
                        id: id,
                        data: response.data
                    };
                    this.$store.commit(
                        "compare/setWidgetDataEmbedding1d",
                        mutationObject
                    );
                }
            }
        },
        fetchEmbeddingOverlays: async function(id, overlayIndex) {
            if (overlayIndex != "density") {
                var queryObject = {
                    id: id,
                    overlayIndex: overlayIndex
                };
                if (
                    this.$store.getters["compare/embedding1dDataExists"](
                        queryObject
                    )
                ) {
                    return this.$store.getters[
                        "compare/getWidgetDataEmbedding1d"
                    ](queryObject);
                }
                // overlay data does not exist, check whether request has been dispatched
                let url = `embeddingIntervalData/${id}/${overlayIndex}/`;
                let requestData = this.$store.getters["compare/getRequest"](
                    url
                );
                let response;
                if (!requestData) {
                    // request has not been dispatched => put it in store
                    this.$store.commit("compare/setRequest", {
                        url: url,
                        data: this.fetchData(url)
                    });
                    response = await this.$store.getters["compare/getRequest"](
                        url
                    );
                    // save it in store -> only first request needs to persist it
                    var mutationObject = {
                        id: id,
                        overlayIndex: overlayIndex,
                        data: response.data["data"]
                    };
                    this.$store.commit(
                        "compare/setWidgetDataEmbedding1d",
                        mutationObject
                    );
                }
            }
        },
        fetchEmbeddingData: async function(id, overlayIndex) {
            await this.fetchEmbeddingPoints(id);
            await this.fetchEmbeddingOverlays(id, overlayIndex);
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

.full-width-flexbox-center {
    display: flex;
    justify-content: center;
    width: 100%;
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
