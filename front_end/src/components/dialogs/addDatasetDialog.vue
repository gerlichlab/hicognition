<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Add Dataset </md-dialog-title>
            <addDatasetForm
                @close-dialog="$emit('close-dialog')"
            ></addDatasetForm>
        </md-dialog>
    </div>
</template>

<script>
import addDatasetForm from "../forms/addDatasetForm";

export default {
    name: "DialogCustom",
    components: {
        addDatasetForm
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 1000px;
}

.md-dialog-actions {
    display: inline;
}
</style>
