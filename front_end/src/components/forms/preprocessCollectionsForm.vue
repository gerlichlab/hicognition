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
                    <!-- Collections -->
                    <div class="md-layout md-gutter">
                        <div class="md-layout-item md-small-size-100">
                            <md-field
                                :class="getValidationClass('collectionID')"
                            >
                                <label for="collectionID">Collections</label>
                                <md-select
                                    name="collectionID"
                                    id="collectionID"
                                    v-model="form.collectionID"
                                    availableDatasets
                                    :disabled="!collectionsAvailable"
                                    required
                                >
                                    <md-option
                                        v-for="item in availableCollections"
                                        :value="item.id"
                                        :key="item.id"
                                        >{{ item.name }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.collectionID.required"
                                    >A collection name is required</span
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
                        @click="fetchDatasets();fetchCollections()"
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
    props: {
        datatype: String
    },
    data: () => ({
        availableCollections: [],
        availableBedFiles: [],
        form: {
            collectionID: null,
            bedfileIDs: [],
        },
        datasetSaved: false,
        sending: false
    }),
    computed: {
        collectionsAvailable: function() {
            return this.availableCollections.length != 0;
        },
        bedFilesAvailable: function() {
            return this.availableBedFiles.length != 0;
        }
    },
    validations: {
        // validators for the form
        form: {
            collectionID: {
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
                // update bedfiles
                this.availableBedFiles = response.data.filter(
                    element =>
                        element.filetype == "bedfile" &&
                        element.processing_state == "finished"
                );
            });
        },
        fetchCollections: function(){
            this.fetchData("collections/").then(response => {
                // update bedfiles
                this.availableCollections = response.data.filter(
                    element => 
                        element.kind == this.datatype
                )
            })
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
            this.postData("preprocess/collections/", formData).then(response => {
                if (response) {
                    this.datasetSaved = true;
                }
                this.sending = false;
                this.clearForm();
            });
        },
        prepare_form_data() {
            // put data into form
            var form_data = {};
            form_data["collection_id"] = JSON.stringify(this.form["collectionID"]);
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
        this.fetchCollections()
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