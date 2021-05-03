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

export default {
    name: "MySessionsDialog",
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
        handleSessionRestoration: function(){
            this.$store.commit("compare/setWidgetCollections", JSON.parse(this.selected_session_object))
            this.$emit("close-dialog")
        },
        handleSelectionAvailable: function(e){
            this.showRestore = true,
            this.selected_session_object = e
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
