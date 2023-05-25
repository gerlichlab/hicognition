<template>
    <div class="spinner-container">
        <div style="height: 500px" v-if="showLoad">
            <md-progress-spinner
                :md-diameter="400"
                :md-stroke="15"
                md-mode="indeterminate"
            ></md-progress-spinner>
        </div>
        <div>
            <span class="md-display-1" v-if="showLoad">
                Session is being restored!
            </span>
            <span class="md-display-1" v-else>
                Session credentials are not valid
            </span>
        </div>
    </div>
</template>

<script>
import { apiMixin } from "../mixins";

export default {
    name: "sessionLoad",
    mixins: [apiMixin],
    data: function() {
        return {
            sessionToken: null,
            sessionID: null,
            showLoad: false
        };
    },
    methods: {
        parseQueryString: function() {
            let queryObject = this.$route.query;
            if ("sessionToken" in queryObject && "sessionID" in queryObject) {
                this.sessionToken = queryObject["sessionToken"];
                this.sessionID = queryObject["sessionID"];
                // commit session token to store
                this.$store.commit("setSessionToken", this.sessionToken);
                this.loadData();
            }
        },
        fetchDatasets: async function() {
            var response = await this.fetchData("datasets/");
            this.$store.commit("setDatasets", response.data);
        },
        loadData: async function() {
            // get session data
            var response = await this.fetchData(`sessions/${this.sessionID}/`);
            if (!response) {
                return;
            }
            this.showLoad = true;
            var parsed_object = JSON.parse(response.data["session_object"]);
            // get dependent data
            for (let collection of Object.values(parsed_object)) {
                for (let child of Object.values(collection)) {
                    for (let child_vals of Object.values(child)) {
                        if (child_vals.widgetDataRef) {
                            var widgetType = child_vals.widgetType;
                            switch (widgetType) {
                                case "Lineprofile":
                                    let refs;
                                    if (child_vals['collectionConfig']['isPairedEnd']){
                                        refs = child_vals.widgetDataRef.map((val) => val[child_vals.selectedSide])
                                    }else{
                                        refs = child_vals.widgetDataRef
                                    }
                                    await this.fetchLineProfileData(
                                        refs
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
            // set widget collections in store
            this.$store.commit("compare/setWidgetCollections", parsed_object);
            // fetch datasets
            await this.fetchDatasets();
            // naviage to compare route
            setTimeout(() => {
                this.$router.push("/main/compare");
            }, 1000);
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
        }
    },
    created: function() {
        this.parseQueryString();
    }
};
</script>

<style scoped>
.spinner-container {
    display: flex;
    justify-content: center;
    align-content: center;
    align-items: center;
    height: 800px;
    flex-direction: column;
}
</style>
