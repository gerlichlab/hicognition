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
                    <!-- Intervals for which annotations are added; first row -->
                    <div class="md-layout md-gutter">
                        <!-- Regions -->
                        <div class="md-layout-item md-layout md-gutter md-alignment-center-center md-small-size-100">

                            <div class="md-layout-item md-size-50">
                                <md-button
                                    class="md-raised md-primary"
                                    @click="startDatasetSelection"
                                    :disabled="!bedFilesAvailable"
                                    >Select Region</md-button
                                >
                            </div>
                            <div class="md-layout-item md-size-50" v-if="form.datasetID" >
                                <span class="md-body-1">{{ regionName }}</span>
                            </div>
                            <div class="md-layout-item md-size-50" v-else>
                                <span
                                    style="color: red; "
                                    v-if="!$v.form.datasetID.required && $v.form.datasetID.$dirty"
                                    >Regions are required</span
                                >
                            </div>
                        </div>
                    </div>
                    <!-- Target file and separator; Second row -->
                    <div class="md-layout md-gutter">
                        <!-- file field -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('file')">
                                <label for="file">File</label>
                                <md-file
                                    id="file"
                                    name="file"
                                    v-model="form.file"
                                    :disabled="sending"
                                    @change="handleFileChange"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.file.required"
                                    >A file is required</span
                                >
                            </md-field>
                        </div>
                    </div>
                    <!-- Separator Fields -->
                    <md-field :class="getValidationClass('separator')">
                        <label for="separator">Text-file separator</label>
                        <md-select
                            name="separator"
                            id="separator"
                            v-model="form.separator"
                            md-dense
                            required
                        >
                            <md-option
                                v-for="item in separators"
                                :value="item.value"
                                :key="item.value"
                                >{{ item.name }}</md-option
                            >
                        </md-select>
                        <span
                            class="md-error"
                            v-if="!$v.form.separator.required"
                            >A separator is required</span
                        >
                    </md-field>
                </md-card-content>
                <!-- Progress bar -->
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <!-- Buttons for submission and closing -->
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit dataset</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >Metadata was added succesfully</md-snackbar
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
    name: "AddMetadataForm",
    mixins: [validationMixin, apiMixin],
    data: () => ({
        form: {
            datasetID: null,
            file: null,
            separator: null
        },
        availableBedFiles: [],
        separators: [
            { name: "Comma", value: "," },
            { name: "Semicolon", value: ";" },
            { name: "Tab", value: "tab" }
        ],
        datasetSaved: false,
        sending: false,
        selectedFile: null,
        expectSelection: false
    }),
    validations: {
        // validators for the form
        form: {
            datasetID: {
                required
            },
            file: {
                required
            },
            separator: {
                required
            }
        }
    },
    computed: {
        regionName: function() {
            if (this.form.datasetID) {
                return this.availableBedFiles.filter(el => el.id === this.form.datasetID)[0].dataset_name
            }
            return undefined
        },
        bedFilesAvailable: function() {
            return this.availableBedFiles.length != 0;
        }
    },
    methods: {
        startDatasetSelection: function () {
            this.expectSelection = true;
            let preselection = this.form.datasetID ? [this.form.datasetID] : []
            EventBus.$emit("show-select-dialog", this.availableBedFiles, "bedfile", preselection);
        },
        registerSelectionEventHandlers: function(){
            EventBus.$on("dataset-selected", this.handleDataSelection)
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion)
        },
        removeSelectionEventHandlers: function(){
            EventBus.$off("dataset-selected", this.handleDataSelection)
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion)
        },
        handleDataSelection: function(id){
            console.log("IE")
            if (this.expectSelection){
                    this.form.datasetID = id
                    this.expectSelection = false
            }
        },
        hanldeSelectionAbortion: function(){
            this.expectSelection = false
        },
        getDatasets: function() {
            // fetches available datasets (cooler and bedfiles) from server
            this.availableBedFiles = this.$store.state.datasets.filter(
                    element =>
                        element.filetype == "bedfile" &&
                        element.processing_state == "finished"
            );
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
        handleFileChange(event) {
            // get file IO-stream
            this.selectedFile = event.target.files[0];
        },
        clearForm() {
            this.$v.$reset();
            this.form.datasetID = null;
            this.form.file = null;
            this.form.separator = null;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                if (key == "file") {
                    // file data needs to be included like this because the form data only contains the filename at this stage
                    formData.append(
                        key,
                        this.selectedFile,
                        this.selectedFile.name
                    );
                } else {
                    formData.append(key, this.form[key]);
                }
            }
            // API call including upload is made in the background
            this.postData("bedFileMetadata/", formData).then(response => {
                if ("ValidationError" in response.data) {
                    this.$emit("form-error", "Rownumber is not compatible!");
                    this.sending = false;
                    this.clearForm();
                } else if (response.data["field_names"].length == 0) {
                    this.$emit(
                        "form-error",
                        "File contains no numeric columns!"
                    );
                    this.sending = false;
                    this.clearForm();
                } else {
                    this.datasetSaved = true;
                    this.sending = false;
                    this.clearForm();
                    this.$emit("success", response.data);
                }
            });
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    created: function() {
        this.getDatasets();
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
