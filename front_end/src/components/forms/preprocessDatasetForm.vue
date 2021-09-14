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
                    <div class="md-layout md-gutter">

                        <div class="md-layout-item md-layout md-gutter md-alignment-center-left md-small-size-50">

                            <div class="md-layout-item md-size-50">
                                <md-button
                                    class="md-raised md-primary"
                                    @click="startRegionSelection"
                                    :disabled="!datasetsAvailable"
                                    >Select Region</md-button
                                >
                            </div>
                            <div class="md-layout-item md-size-50" >
                                <span class="md-body-1"> {{ numberRegions }} {{ pluralizedRegions }} selected</span>
                            </div>
                            <div class="md-layout-item md-size-50">
                                <span
                                    style="color: red; "
                                    v-if="!$v.form.bedfileIDs.required && $v.form.bedfileIDs.$dirty"
                                    >At least one region is required</span
                                >
                            </div>
                        </div>

                        <div class="md-layout-item md-layout md-gutter md-alignment-center-left md-small-size-50">

                            <div class="md-layout-item md-size-50">
                                <md-button
                                    class="md-raised md-primary"
                                    @click="startFeatureSelection"
                                    :disabled="!datasetsAvailable || this.form.bedfileIDs.length === 0 || !this.preprocessingMapLoaded"
                                    >Select Features</md-button
                                >
                            </div>
                            <div class="md-layout-item md-size-50">
                                <span class="md-body-1">{{ numberFeatures }} features selected</span>
                            </div>
                            <div class="md-layout-item md-size-50">
                                <span
                                    style="color: red; "
                                    v-if="!$v.form.bedfileIDs.required && $v.form.bedfileIDs.$dirty"
                                    >At least one feature dataset is required</span
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
import EventBus from "../../eventBus";

export default {
    name: "PreprocessDatasetForm",
    mixins: [validationMixin, apiMixin, formattingMixin],
    data: () => ({
        availableDatasets: [],
        availableCoolers: [],
        availableBigwigs: [],
        availableBedFiles: [],
        finishedDatasets: [],
        processingDatasets: [],
        failedDatasets: [],
        form: {
            datasetIDs: [],
            bedfileIDs: [],
        },
        datasetSaved: false,
        sending: false,
        preprocessingMapLoaded: false
    }),
    computed: {
        numberRegions: function(){
            return this.form.bedfileIDs.length
        },
        pluralizedRegions: function(){
            return this.numberRegions == 0 ? "regions" : "region"
        },
        numberFeatures: function(){
            return this.form.datasetIDs.length
        },
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
        regionIDs: function(){
            return this.availableBedFiles.map(el => el.id)
        },
        selectedAssembly: function(){
            if (this.form.bedfileIDs.length !== 0){
                return this.availableBedFiles.filter(el => el.id === this.form.bedfileIDs[0])[0].assembly
            }
        }
    },
    validations: {
        // validators for the form
        form: {
            datasetIDs: {
                required
            },
            bedfileIDs: {
                required
            }
        }
    },
    methods: {
        startRegionSelection: function () {
            this.expectSelection = true;
            let preselection = [...this.form.bedfileIDs]
            EventBus.$emit("show-select-dialog", this.availableBedFiles, "bedfile", preselection, true);
        },
        startFeatureSelection: function () {
            this.expectSelection = true;
            let preselection = [...this.form.datasetIDs]
            let datasets = this.availableBigwigs.concat(this.availableCoolers)
            EventBus.$emit("show-select-dialog", datasets, "features", preselection, false, this.selectedAssembly, this.finishedDatasets, this.processingDatasets, this.failedDatasets);
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
            if (this.expectSelection){
                if (this.isRegionSelection(ids)){
                    // blank features
                    this.form.datasetIDs = []
                    // blanck preprocessing map
                    this.preprocessingMapLoaded = false
                    this.form.bedfileIDs = [ids]
                    // get preprocess dataset map
                    this.fetchPreprocessData(ids).then((response) => {
                        let bigwigIDs = Object.keys(response.data["lineprofile"]).map(el => Number(el))
                        let coolerIDs = Object.keys(response.data['pileup']).map(el => Number(el))
                        let collectiveIDs = bigwigIDs.concat(coolerIDs)
                        this.finishedDatasets = this.finishedDatasets.concat(collectiveIDs)
                        this.preprocessingMapLoaded = true
                    })
                    // set processing datasets and failed datasets
                    this.processingDatasets = this.getBedDataset(ids).processing_datasets
                    this.failedDatasets = this.getBedDataset(ids).failed_datasets
                } else {
                    this.form.datasetIDs = ids
                }
                this.expectSelection = false
                }
        },
        hanldeSelectionAbortion: function(){
            this.expectSelection = false
        },
        isRegionSelection: function(ids) {
            return this.regionIDs.includes(ids)
        },
        getBedDataset: function(id){
            return this.availableBedFiles.filter(el => el.id === id)[0]
        },
        getDatasets: function() {
            // fetches available datasets (cooler and bedfiles) from server
            this.availableDatasets = this.$store.state.datasets.filter(
                    element =>
                        (element.filetype == "cooler" ||
                            element.filetype == "bigwig") &&
                        element.processing_state != "uploading"
                );
                this.availableCoolers = this.$store.state.datasets.filter(
                    element =>
                        element.filetype == "cooler" &&
                        element.processing_state != "uploading"
                );
                this.availableBigwigs = this.$store.state.datasets.filter(
                    element =>
                        element.filetype == "bigwig" &&
                        element.processing_state != "uploading"
                );
                this.availableBedFiles = this.$store.state.datasets.filter(
                    element =>
                        element.filetype == "bedfile" &&
                        element.processing_state == "finished"
            );
        },
        fetchPreprocessData: function(regionID){
            // get availability object
            return this.fetchData(`datasets/${regionID}/processedDataMap/`)
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
            form_data["dataset_ids"] = JSON.stringify(this.form["datasetIDs"]);
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
        this.getDatasets();
        this.registerSelectionEventHandlers()
    },
    beforeDestroy: function(){
        this.removeSelectionEventHandlers()
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
