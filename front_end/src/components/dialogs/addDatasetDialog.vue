<template>
    <div>
        <b-modal
            v-model="showDialog"
            size="xl"
            modal-class="modal-90vh"
            scrollable
            centered
        >
            <template v-slot:modal-title>
                {{ welcomeMessage }}
            </template>
            <b-tabs content-class="mt-3">
                <b-tab title="Single">
                        <add-dataset-form
                            @close-dialog="$emit('close-dialog')"
                            @dataset-saved-finished="allowSubmit = true;"
                            :datasetType="datatype"
                            ref="addDatasetForm"
                        ></add-dataset-form>
                </b-tab>
                <b-tab title="Bulk">
                    <add-dataset-stepper
                        @close-dialog="$emit('close-dialog')"
                        :datasetType="datatype"
                        :fileTypeMapping="fileTypeMapping"
                    >
                    </add-dataset-stepper>
                </b-tab>
            </b-tabs>
            <template v-slot:modal-footer>
                <b-button @click="$emit('close-dialog')">Close</b-button>
                <b-button @click="handleSubmit" :disabled="!allowSubmit">Submit</b-button>
            </template>
        </b-modal>
    </div>
</template>

<script>
import addDatasetForm from "../forms/addDatasetForm";
import addDatasetStepper from "../ui/addDatasetStepper.vue";
import { apiMixin } from "../../mixins";

export default {
    name: "AddDatasetDialog",
    components: {
        addDatasetForm,
        addDatasetStepper
    },
    mixins: [apiMixin],
    props: {
        dialog: Boolean,
        datatype: String // region or feature
    },
    data: () => ({
        fileTypes: null,
        allowSubmit: true
    }),
    methods: {
        handleSubmit() {
            this.allowSubmit = false;
            this.$refs.addDatasetForm.validateDataset();
        }
    },
    computed: {
        welcomeMessage: function() {
            if (this.datatype == "feature") {
                return "Add genomic feature";
            } else if (this.datatype == "region") {
                return "Add genomic region";
            } else {
                return "Add dataset";
            }
        },
        fileTypeMapping: function() {
            if (this.datatype == "feature") {
                return {
                    mcool: "cooler",
                    bw: "bigwig",
                    bigwig: "bigwig",
                    bigWig: "bigwig"
                };
            } else if (this.datatype == "region") {
                return {
                    bed: "bedfile"
                };
            } else {
                return {
                    bed: "bedfile",
                    mcool: "cooler",
                    bw: "bigwig",
                    bigwig: "bigwig",
                    bigWig: "bigwig"
                };
            }
        },
        showDialog: {
            get() {
                return this.dialog;
            },
            set(value) {
                this.$emit('close-dialog');
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.mainText {
    display: block;
    width: 5vw;
    min-width: 400px;
    text-align: justify;
    text-justify: inter-word;
    word-wrap: break-word;
    white-space: normal;
}

.modal-90vh {
    max-height: 90vh;
}
</style>
