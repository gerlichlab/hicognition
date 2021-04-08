<template>
    <div>
        <!-- Form definition -->
        <form
            novalidate
            class="md-layout"
            @submit.prevent="validateDataset"
            enctype="multipart/form-data"
        >
            <md-card class="md-layout-item">
                <!-- Field definitions -->
                <md-card-content>
                    <!-- Cooler file and binsizes; first row -->
                    <div class="md-layout md-gutter">
                        <!-- cooler file -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('datasetID')">
                                <label for="datasetID">Genomic Dataset</label>
                                <md-select
                                    name="datasetID"
                                    id="datasetID"
                                    v-model="form.datasetID"
                                    availableDatasets
                                    :disabled="!datasetsAvailable"
                                    required
                                >
                                    <md-option
                                        v-for="item in availableDatasets"
                                        :value="item.id"
                                        :key="item.id"
                                        >{{ item.dataset_name }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.datasetID.required"
                                    >A dataset name is required</span
                                >
                            </md-field>
                        </div>
                        <!-- Binsizes field -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('binsizes')">
                                <label for="binsizes">Binsizes</label>
                                <md-select
                                    name="binsizes"
                                    id="binsizes"
                                    v-model="form.binsizes"
                                    required
                                    multiple
                                >
                                    <md-option
                                        v-for="item in availableBinsizes"
                                        :value="item"
                                        :key="item"
                                        >{{
                                            convertBasePairsToReadable(item)
                                        }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.binsizes.required"
                                    >Binsize selection is required</span
                                >
                            </md-field>
                        </div>
                    </div>
                    <!-- Second row -->
                    <div class="md-layout md-gutter">
                        <!-- bedfiles -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('bedfileIDs')">
                                <label for="bedfileIDs">Regions</label>
                                <md-select
                                    name="bedfileIDs"
                                    id="bedfileIDs"
                                    v-model="form.bedfileIDs"
                                    md-dense
                                    :disabled="!bedFilesAvailable"
                                    required
                                    multiple
                                >
                                    <md-option
                                        v-for="item in availableBedFiles"
                                        :value="item.id"
                                        :key="item.id"
                                        >{{ item.dataset_name }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.bedfileIDs.required"
                                    >Regions are required</span
                                >
                            </md-field>
                        </div>
                        <!-- windwosize -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field
                                :class="getValidationClass('windowsizes')"
                            >
                                <label for="windowsizes">Windowsizes</label>
                                <md-select
                                    id="windowsizes"
                                    name="windowsizes"
                                    v-model="form.windowsizes"
                                    md-dense
                                    :disabled="!intervalsAvailable"
                                    required
                                    multiple
                                >
                                    <md-option
                                        v-for="item in availableIntervals"
                                        :value="item.windowsize"
                                        :key="item.windowsize"
                                        >{{
                                            convertBasePairsToReadable(
                                                item.windowsize
                                            )
                                        }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.windowsizes.required"
                                    >A windowsize is required!</span
                                >
                            </md-field>
                        </div>
                    </div>
                </md-card-content>
                <!-- Progress bar -->
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <!-- Buttons for submission and closing -->
                <md-card-actions>
                    <md-button
                        class="md-dense md-raised md-primary md-icon-button md-alignment-horizontal-left"
                        @click="fetchDatasets"
                    >
                        <md-icon>cached</md-icon>
                    </md-button>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit job</md-button
                    >
                    <md-button class="md-primary" @click="$emit('close-dialog')"
                        >Close</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >Preprocessing was started successfully!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin, formattingMixin } from "../../mixins";
import { group_intervals_on_windowsize } from "../../functions";

export default {
    name: "preprocessDatasetForm",
    mixins: [validationMixin, apiMixin, formattingMixin],
    data: () => ({
        availableDatasets: [],
        availableCoolers: [],
        availableBigwigs: [],
        availableBinsizes: [500, 1000, 5000, 10000, 20000, 50000],
        availableBedFiles: [],
        availableIntervals: [],
        form: {
            datasetID: null,
            binsizes: [],
            bedfileIDs: [],
            windowsizes: []
        },
        datasetSaved: false,
        sending: false
    }),
    computed: {
        datasetsAvailable: function() {
            return this.availableDatasets.length != 0;
        },
        coolersAvailable: function() {
            return this.availableCoolers.length != 0;
        },
        bigwigsAvailable: function() {
            return this.availableBigwigs.length != 0;
        },
        bedFilesAvailable: function() {
            return this.availableBedFiles.length != 0;
        },
        intervalsAvailable: function() {
            return Object.keys(this.availableIntervals).length != 0;
        }
    },
    validations: {
        // validators for the form
        form: {
            datasetID: {
                required
            },
            binsizes: {
                required
            },
            bedfileIDs: {
                required
            },
            windowsizes: {
                required
            }
        }
    },
    methods: {
        fetchDatasets: function() {
            // fetches available datasets (cooler and bedfiles) from server
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                this.$store.commit("setDatasets", response.data);
                // update datasets
                this.availableDatasets = response.data.filter(
                    element =>
                        (element.filetype == "cooler" ||
                            element.filetype == "bigwig") &&
                        element.processing_state != "uploading"
                );
                this.availableCoolers = response.data.filter(
                    element =>
                        element.filetype == "cooler" &&
                        element.processing_state != "uploading"
                );
                this.availableBigwigs = response.data.filter(
                    element =>
                        element.filetype == "bigwig" &&
                        element.processing_state != "uploading"
                );
                this.availableBedFiles = response.data.filter(
                    element =>
                        element.filetype == "bedfile" &&
                        element.processing_state == "finished"
                );
            });
        },
        fetchPileupregions: async function() {
            // fetches available intervals or selected bedfiles
            var intervals = [];
            var tempPileupRegions = {};
            for (var regionID of this.form.bedfileIDs) {
                tempPileupRegions = await this.fetchPileupregion(regionID);
                intervals.push(...tempPileupRegions.data);
            }
            this.availableIntervals = group_intervals_on_windowsize(intervals);
        },
        fetchPileupregion: function(regionID) {
            // fetches intervals for one bedfile
            return this.fetchData(`datasets/${regionID}/intervals/`);
        },
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.form[fieldName];

            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty
                };
            }
        },
        clearForm() {
            this.$v.$reset();
            for (var key in this.form) {
                // vue introduces a watches into arrays that does not allow blanking
                if (Array.isArray(this.form[key])) {
                    this.form[key] = [];
                } else {
                    this.form[key] = null;
                }
            }
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // prepare data for form
            var prepared_data = this.prepare_form_data();
            // construct form data
            var formData = new FormData();
            for (var key in prepared_data) {
                formData.append(key, prepared_data[key]);
            }
            console.log(formData);
            // API call including upload is made in the background
            this.postData("preprocess/", formData);
            //TODO: make conditional on promise
            // show progress bar for 1.5 s
            window.setTimeout(() => {
                this.datasetSaved = true;
                this.sending = false;
                this.clearForm();
            }, 1500);
        },
        prepare_form_data() {
            // prepare intervals
            var intervals_ids = [];
            for (var windowsize of this.form["windowsizes"]) {
                intervals_ids.push(...this.availableIntervals[windowsize].id);
            }
            // put data into form
            var form_data = {};
            form_data["interval_ids"] = JSON.stringify(intervals_ids);
            form_data["dataset_id"] = JSON.stringify(this.form["datasetID"]);
            form_data["binsizes"] = JSON.stringify(this.form["binsizes"]);
            return form_data;
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    watch: {
        "form.bedfileIDs": function() {
            this.fetchPileupregions();
        }
    },
    created: function() {
        this.fetchDatasets();
    }
};
</script>

<style lang="scss" scoped>
.md-progress-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
}
</style>