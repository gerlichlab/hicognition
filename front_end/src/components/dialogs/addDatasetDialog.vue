<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >{{ welcomeMessage }}

                <md-icon
                    >info

                    <md-tooltip md-direction="right">
                        <div>
                            <span class="md-title"
                                >Information about addition of data</span
                            >
                        </div>
                        <div class="mainText">
                            <p>
                                <span class="md-subheading">
                                    Datasets can either be genomic intervals or
                                    genomic features. Genomic intervals can be
                                    added int form of bedfiles and genomic
                                    features can be added either in the form of
                                    cooler files (.mcool) or bigwig files.
                                </span>
                            </p>
                            <br />
                            <p>
                                <span class="md-subheading">
                                    The added files need to conform to certain
                                    formatting standards to ensure
                                    compatibility. For bedfiles, the first three
                                    columns need to be
                                    <b>(chrom, start, end)</b> and specify the
                                    chromosome, start-position and end-position
                                    of a feature. In addition, chromosomes need
                                    to be in the hg19 genome and not be any of
                                    the small contigs (only chr${specifier} is
                                    accepted, where specified is either a number
                                    from 1 to 22 or one of X or Y).
                                </span>
                            </p>
                            <br />
                            <p>
                                <span class="md-subheading">
                                    For mcooler files, the following resolutions
                                    need to be available:
                                    <b
                                        >[1000, 2000, 5000, 10000,20000,50000,
                                        100000, 200000]</b
                                    >. For bigwig files, no formatting
                                    requirement is enforced other than one
                                    should be able to open them with pybbi. Note
                                    however that if a binsize is not availalbe,
                                    the respective plot will not show any data.
                                </span>
                            </p>
                        </div>
                    </md-tooltip>
                </md-icon>
            </md-dialog-title>
            <md-dialog-content>
                <md-tabs class="md-primary">
                    <md-tab id="tab-single" md-label="Single">
                        <div
                            style="
                                overflow: auto;
                                max-height: 600px;
                                padding: 10px;
                            "
                        >
                            <addDatasetForm
                                @close-dialog="$emit('close-dialog')"
                                :datasetType="datatype"
                            ></addDatasetForm>
                        </div>
                    </md-tab>
                    <md-tab id="tab-bulk" md-label="Bulk">
                        <addDatasetStepper
                            @close-dialog="$emit('close-dialog')"
                            :datasetType="datatype"
                            :fileTypeMapping="fileTypeMapping"
                        >
                        </addDatasetStepper>
                    </md-tab>
                </md-tabs>
            </md-dialog-content>
        </md-dialog>
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
        fileTypes: null
    }),
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
        showDialog: function() {
            return this.dialog;
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog-content {
    padding: 0px;
    min-width: 60vw;
    min-height: 60vh;
}

.mainText {
    display: block;
    width: 5vw;
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
