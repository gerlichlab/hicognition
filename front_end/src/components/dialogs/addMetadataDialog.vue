<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Add Metadata
                <md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about addition of metadata</span
                        >
                    </div>
                    <div v-for="(item, index) in addMetadataText" :key="index">
                        <span class="md-subheading">{{ item }}</span>
                    </div>
                </md-tooltip>
            </md-dialog-title>
            <addMetadataStepper
                @close-dialog="$emit('close-dialog')"
            ></addMetadataStepper>
        </md-dialog>
    </div>
</template>

<script>
import addMetadataStepper from "../ui/addMetadataStepper";

export default {
    name: "DialogCustom",
    data: function() {
        return {
            addMetadataText: "Here you can add metadata for your uploaded region files. \n You can upload textfiles that have the same number of rows as your target regionfile. \n Only numeric columns will be displayed. \n Looking forward to your metadata.".split(
                "\n"
            )
        };
    },
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

.md-tooltip {
    height: auto;
}

.md-dialog-actions {
    display: inline;
}
</style>
