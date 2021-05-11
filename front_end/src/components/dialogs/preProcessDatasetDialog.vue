<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Preprocess Dataset<md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about preprocessing</span
                        >
                    </div>
                    <div
                        v-for="(item, index) in preprocessDataSetText"
                        :key="index"
                    >
                        <span class="md-subheading">{{ item }}</span>
                    </div>
                </md-tooltip>
            </md-dialog-title>
            <preprocessDatasetForm
                @close-dialog="$emit('close-dialog')"
            ></preprocessDatasetForm>
        </md-dialog>
    </div>
</template>

<script>
import preprocessDatasetForm from "../forms/preprocessDatasetForm";

export default {
    name: "PreprocessDatasetDialog",
    components: {
        preprocessDatasetForm
    },
    data: function() {
        return {
            preprocessDataSetText: "\nThis form allows you to preproces datasets. \n Binsize selections and windowsize selections are validated \n to not cause problems in downstream processing. \n First, the produced matrices cannot be too large, \n meaning that you should not select too small \n binsizes with large windowsizes. \n Second, if preprocessing coolers, windowsizes need \n to be divisible by windowsizes. \n\n\n Happy preprocessing!".split(
                "\n"
            )
        };
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
