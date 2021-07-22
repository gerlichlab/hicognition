<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Available Collections</md-dialog-title>
            <md-content class="content">
                <collection-table
                    @selection-available="handleSelectionAvailable"
                    @selection-unavailable="handleSelectionUnAvailable"
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
            showDelete: false
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
        handleSessionDeletion: function() {
            this.deleteData(`collections/${this.selected_session_id}/`).then(
                response => {
                    EventBus.$emit("fetch-sessions");
                }
            );
        },
        handleSelectionAvailable: function(session_id) {
                this.selected_session_id = session_id;
                this.showDelete = true
        },
        handleSelectionUnAvailable: function() {
            (this.showDelete = false);
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 80vw;
}

.full-width-flexbox-center{
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
