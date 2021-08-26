<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Available Genome Assemblies</md-dialog-title>
            <md-content class="content">
                <assemblyTable
                    @selection-available="handleSelectionAvailable"
                    @selection-unavailable="handleSelectionUnAvailable"
                />
            </md-content>
            <md-dialog-actions>
                <div class="full-width">
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
import assemblyTable from "../tables/assemblyTable";
import { apiMixin } from "../../mixins";

export default {
    name: "collectionsDialog",
    mixins: [apiMixin],
    data: function() {
        return {
            selected_assembly_id: null,
            showDelete: false
        };
    },
    components: {
        assemblyTable
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
        handleAssemblyDeletion: function() {
            return
        },
        handleSelectionAvailable: function(assembly_id) {
                this.selected_assembly_id = assembly_id;
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
