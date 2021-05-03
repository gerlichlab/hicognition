<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Available Sessions</md-dialog-title>
            <md-content class="content">
                <sessionsTable @selection-available="handleSelectionAvailable" @selection-unavailable="handleSelectionUnAvailable"></sessionsTable>
            </md-content>
            <md-dialog-actions>
                <md-button class="md-primary" @click="handleSessionRestoration" v-if="showRestore"
                    >Restore</md-button
                >
                <md-button class="md-primary" @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>

<script>
import sessionsTable from "../tables/sessionsTable";
import {apiMixin} from "../../mixins";

export default {
    name: "MySessionsDialog",
    mixins: [apiMixin],
    data: function() {
        return {
            showRestore: false,
            selected_session_object: null
        }
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
        }
    },
    methods: {
        handleSessionRestoration: async function(){
            // fetch data references to put into store
            var parsed_object = JSON.parse(this.selected_session_object);
            for (let collection of Object.values(parsed_object)){
                for (let child of Object.values(collection)){
                    for(let child_vals of Object.values(child)){
                        if (child_vals.widgetDataRef){
                            var widgetType = child_vals.widgetType;
                            switch (widgetType){
                                case "Lineprofile":
                                    await this.fetchLineProfileData(child_vals.widgetDataRef)
                                    break
                                case "Pileup":
                                    await this.fetchPileupData(child_vals.widgetDataRef)
                                    break
                                case "Stackup":
                                    await this.fetchStackupData(child_vals.widgetDataRef)
                            }
                        }
                    }
                }
            }
            this.$store.commit("compare/setWidgetCollections", JSON.parse(this.selected_session_object))
            this.$emit("close-dialog")
        },
        handleSelectionAvailable: function(e){
            this.showRestore = true,
            this.selected_session_object = e
        },
        fetchLineProfileData: async function(ids){
            for (let id of ids){
                // checks whether lineprofile data is in store and does not fetch it if it is there
                if (this.$store.getters["compare/lineprofileExists"](id)) {
                    continue
                }
                var response = await this.fetchData(`averageIntervalData/${id}/`);
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
        fetchStackupData: async function(id){
            // checks whether pileup data is in store and fetches it if it is not
            var queryObject = {
                id: id
            };
            if (this.$store.getters["compare/stackupExists"](queryObject)) {
                return
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
        fetchPileupData: async function(dataRef){
            for (let [pileupType, id] of Object.entries(dataRef)){
                // checks whether pileup data is in store and fetches it if it is not
                var queryObject = {
                    pileupType: pileupType,
                    id: id
                };
                console.log(queryObject);
                if (this.$store.getters["compare/pileupExists"](queryObject)) {
                    return
                }
                // pileup does not exists in store, fetch it
                var response = await this.fetchData(`averageIntervalData/${id}/`);
                var parsed = response.data;
                // save it in store
                var mutationObject = {
                    pileupType: pileupType,
                    id: id,
                    data: parsed
                };
                this.$store.commit("compare/setWidgetDataPileup", mutationObject);
            }
        },
        handleSelectionUnAvailable: function(){
            this.showRestore = false,
            this.selected_session_object = null
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 80vw;
}

.content {
    margin: 10px;
}
</style>
