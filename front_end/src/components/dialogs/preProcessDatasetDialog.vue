<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Preprocess Datasets<md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about preprocessing</span
                        >
                    </div>
                    <div class="mainText">
                        <p>
                            <span class="md-subheading">
                                This form allows you to preproces datasets.
                                Binsizes and windowsizes are selected
                                automatically based on reasonable presets. Happy
                                preprocessing!
                            </span>
                        </p>
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
import { apiMixin } from "../../mixins";

export default {
    name: "PreprocessDatasetDialog",
    mixins: [apiMixin],
    components: {
        preprocessDatasetForm
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
    },
    watch: {
        dialog: function(val){
            if (val){
                this.fetchAndStoreDatasets()
            }
        }
    }
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
