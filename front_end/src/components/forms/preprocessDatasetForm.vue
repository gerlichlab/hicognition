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
                                    <md-optgroup
                                        label="Coolers"
                                        v-if="coolersAvailable"
                                    >
                                        <md-option
                                            v-for="item in availableCoolers"
                                            :value="item.id"
                                            :key="item.id"
                                            >{{ item.dataset_name }}</md-option
                                        >
                                    </md-optgroup>
                                    <md-optgroup
                                        label="Bigwigs"
                                        v-if="bigwigsAvailable"
                                    >
                                        <md-option
                                            v-for="item in availableBigwigs"
                                            :value="item.id"
                                            :key="item.id"
                                            >{{ item.dataset_name }}</md-option
                                        >
                                    </md-optgroup>
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.datasetID.required"
                                    >A dataset name is required</span
                                >
                            </md-field>
                        </div>
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

export default {
    name: "PreprocessDatasetForm",
    mixins: [validationMixin, apiMixin, formattingMixin],
    data: () => ({
        availableDatasets: [],
        availableCoolers: [],
        availableBigwigs: [],
        availableBedFiles: [],
        form: {
            datasetID: null,
            bedfileIDs: [],
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
        }
    },
    validations: {
        // validators for the form
        form: {
            datasetID: {
                required
            },
            bedfileIDs: {
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
            // API call
            this.postData("preprocess/datasets/", formData).then(response => {
                if (response) {
                    this.datasetSaved = true;
                }
                this.sending = false;
                this.clearForm();
            });
        },
        isCooler(id) {
            // checks wheter a dataset id in this.availableDAtasets is a cooler file
            for (var element of this.availableDatasets) {
                if (element.id == id) {
                    if (element.filetype == "cooler") {
                        return true;
                    }
                    return false;
                }
            }
            return false;
        },
        prepare_form_data() {
            // put data into form
            var form_data = {};
            form_data["dataset_id"] = JSON.stringify(this.form["datasetID"]);
            form_data["region_ids"] = JSON.stringify(this.form["bedfileIDs"]);
            return form_data;
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    created: function() {
        this.fetchDatasets();
    }
};
</script>

<style lang="scss" scoped>
.margin-right {
    margin-right: 10px;
}

.md-progress-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
}

.red {
    color: rgb(255, 23, 68);
}
</style>
