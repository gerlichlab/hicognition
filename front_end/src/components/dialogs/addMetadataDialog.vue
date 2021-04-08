<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Add Metadata </md-dialog-title>
            <addMetadataStepper
                @close-dialog="$emit('close-dialog')"
            ></addMetadataStepper>
        </md-dialog>
    </div>
</template>

<script>
import addMetadataStepper from "../addMetadataStepper";

export default {
    name: "DialogCustom",
    components: {
        addMetadataStepper
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: {
            set: function(value) {
                if (!value) {
                    this.$emit("close-dialog");
                }
            },
            get: function() {
                return this.dialog;
            }
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
