<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Edit Dataset
            </md-dialog-title>
            <md-content class="content">
                <modify-dataset-form
                :datasetID="datasetID"
                />
            </md-content>
            <md-dialog-actions>
                <md-button
                    class="md-secondary"
                    @click="
                        $emit('close-dialog');
                    "
                    >Close</md-button
                >
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>

<script>
import modifyDatasetForm from '../forms/modifyDatasetForm.vue';

export default {
    name: "EditDatasetDialog",
    components: { modifyDatasetForm },
    props: {
        dialog: Boolean,
        datasetID: Number
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        }
    }
};
</script>

<style lang="scss" scoped>

.mainText {
    display: block;
    width: 20vw;
    min-width: 400px;
    text-align: justify;
    text-justify: inter-word;
    word-wrap: break-word;
    white-space: normal;
}

.md-tooltip {
    height: auto;
}

.md-dialog-actions {
    display: inline;
}
</style>
