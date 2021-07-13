<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Add Dataset
                <md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about addition of data</span
                        >
                    </div>
                    <div class="mainText">
                        <p>
                            <span class="md-subheading">
                                Here you can add datasets. Datasets can either
                                be genomic intervals or genomic features.
                                Genomic intervals can be added int form of
                                bedfiles and genomic features can be added
                                either in the form of cooler files (.mcool) or
                                bigwig files.
                            </span>
                        </p>
                        <br />
                        <p>
                            <span class="md-subheading">
                                The added files need to conform to certain
                                formatting standards to ensure compatibility.
                                For bedfiles, the first three columns need to be
                                <b>(chrom, start, end)</b> and specify the
                                chromosome, start-position and end-position of a
                                feature. In addition, chromosomes need to be in
                                the hg19 genome and not be any of the small
                                contigs (only chr${specifier} is accepted, where
                                specified is either a number from 1 to 22 or one
                                of X or Y).
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
                                >. For bigwig files, no formatting requirement
                                is enforced other than one should be able to
                                open them with pybbi. Note however that if a
                                binsize is not availalbe, the respective plot
                                will not show any data.
                            </span>
                        </p>
                    </div>
                    <!-- <div v-for="(item, index) in infoText" :key="index">
                        <span class="md-subheading">{{ item }}</span>
                    </div> -->
                </md-tooltip>
            </md-dialog-title>
            <addDatasetForm
                @close-dialog="$emit('close-dialog')"
            ></addDatasetForm>
        </md-dialog>
    </div>
</template>

<script>
import addDatasetForm from "../forms/addDatasetForm";

export default {
    name: "AddDatasetDialog",
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

.mainText {
    display: block;
    width: 20vw;
    word-wrap: break-word;
    word-break: break-all;
    white-space: normal;
}

.md-tooltip {
    height: auto;
}

.md-dialog-actions {
    display: inline;
}
</style>
