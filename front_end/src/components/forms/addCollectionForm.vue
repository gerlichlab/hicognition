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
                    <!-- Dataset name ande genotyp; first row -->
                    <div class="md-layout md-gutter">
                        <!-- dataset name -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('name')">
                                <label :for="`name_collections-${fileType}`"
                                    >Name</label
                                >
                                <md-input
                                    :name="`name_collections-${fileType}`"
                                    :id="`name_collections-${fileType}`"
                                    v-model="form.name"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.name.required"
                                    >A collection name is required</span
                                >
                            </md-field>
                        </div>
                        <!-- Genotype field -->
                        <div
                            class="md-layout-item md-layout md-gutter md-alignment-center-center md-small-size-100"
                        >
                            <div class="md-layout-item md-size-50">
                                <md-button
                                    class="md-raised md-primary"
                                    @click="startDatasetSelection"
                                    :disabled="sending"
                                    >Select Datasets</md-button
                                >
                            </div>

                            <div
                                class="md-layout-item md-size-50"
                                v-if="form.used_datasets.length !== 0"
                            >
                                <span class="md-body-1">{{ datasetNumber }} datasets selected</span>
                            </div>
                            <div class="md-layout-item md-size-50" v-else>
                                <span
                                    style="color: red; "
                                    v-if="
                                        !$v.form.used_datasets.required &&
                                            $v.form.used_datasets.$dirty
                                    "
                                    >At least one dataset is required!</span
                                >
                            </div>
                        </div>
                    </div>
                </md-card-content>
                <!-- Progress bar -->
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <!-- Buttons for submission and closing -->
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit Collection</md-button
                    >
                    <md-button class="md-primary" @click="$emit('close-dialog')"
                        >Close</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >The collection was added succesfully and is ready for
                preprocessing!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";
import EventBus from "../../eventBus";

export default {
    name: "AddCollectionForm",
    mixins: [validationMixin, apiMixin],
    props: {
        fileType: String
    },
    data: () => ({
        form: {
            name: null,
            used_datasets: []
        },
        datasetSaved: false,
        sending: false,
        availableDatasets: []
    }),
    validations: {
        // validators for the form
        form: {
            name: {
                required
            },
            used_datasets: {
                required
            }
        }
    },
    computed: {
        datasetNumber: function(){
                return this.form.used_datasets.length
        }
    },
    methods: {
        startDatasetSelection: function () {
            this.expectSelection = true;
            let preselection = [...this.form.used_datasets]
            let fileType = this.fileType === "regions" ? "bedfile" : "bigwig"
            EventBus.$emit("show-select-dialog", this.availableDatasets, fileType, preselection, false);
        },
        registerSelectionEventHandlers: function(){
            EventBus.$on("dataset-selected", this.handleDataSelection)
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion)
        },
        removeSelectionEventHandlers: function(){
            EventBus.$off("dataset-selected", this.handleDataSelection)
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion)
        },
        handleDataSelection: function(ids){
            console.log("IE")
            if (this.expectSelection){
                    this.form.used_datasets = ids
                    this.expectSelection = false
            }
        },
        hanldeSelectionAbortion: function(){
            this.expectSelection = false
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
        fetchDatasets: function() {
            // fetches available datasets (cooler and bedfiles) from server
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                this.$store.commit("setDatasets", response.data);
                // update datasets
                this.availableDatasets = response.data.filter(element => {
                    if (this.fileType == "regions") {
                        return element.filetype == "bedfile";
                    } else if (this.fileType == "1d-features") {
                        return element.filetype == "bigwig";
                    } else {
                        return element.filetype == "cooler";
                    }
                });
            });
        },
        clearForm() {
            this.$v.$reset();
            this.form.name = null;
            this.form.used_datasets = [];
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            formData.append("kind", this.fileType);
            formData.append(
                "used_datasets",
                JSON.stringify(this.form.used_datasets)
            );
            formData.append("name", this.form.name);
            // // API call including upload is made in the background
            this.postData("collections/", formData).then(response => {
                this.sending = false;
                this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                }
            });
            setTimeout(() => {
                this.sending = false;
            }, 500);
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    mounted: function() {
        this.fetchDatasets();
        this.registerSelectionEventHandlers()
    },
    beforeDestroy: function(){
        this.removeSelectionEventHandlers()
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
.top-margin {
    margin-top: 24px;
}
</style>
