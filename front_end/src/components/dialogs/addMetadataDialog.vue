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
                    <div class="mainText">
                        <p>
                            <span class="md-subheading">
                                Here you can add metadata for your uploaded
                                region files. You can upload textfiles that have
                                the same number of rows as your target
                                regionfile. Only numeric columns will be
                                displayed.Looking forward to your metadata.
                            </span>
                        </p>
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
    name: "AddMetaDataDialog",
    components: {
        addMetadataStepper,
    },
    props: {
        dialog: Boolean,
    },
    computed: {
        showDialog: {
            set: function (value) {
                if (!value) {
                    this.$emit("close-dialog");
                }
            },
            get: function () {
                return this.dialog;
            },
        },
    },
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 1000px;
}

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
