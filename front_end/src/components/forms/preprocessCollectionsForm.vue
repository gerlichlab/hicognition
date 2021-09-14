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
                        <!-- bedfiles -->
                        <div
                            class="
                                md-layout-item
                                md-layout
                                md-gutter
                                md-alignment-center-center
                                md-small-size-100
                            "
                        >
                            <div class="md-layout-item md-size-50">
                                <md-button
                                    class="md-raised md-primary"
                                    @click="startRegionSelection"
                                    :disabled="!bedFilesAvailable"
                                    >Select Region</md-button
                                >
                            </div>
                            <div
                                class="md-layout-item md-size-50"
                                v-if="form.bedfileIDs.length !== 0"
                            >
                                <span class="md-body-1">{{
                                    this.getBedFileName(this.form.bedfileIDs[0])
                                }}</span>
                            </div>
                            <div class="md-layout-item md-size-50" v-else>
                                <span
                                    style="color: red"
                                    v-if="
                                        !$v.form.bedfileIDs.required &&
                                            $v.form.bedfileIDs.$dirty
                                    "
                                    >At least one dataset is required!</span
                                >
                            </div>
                        </div>
                        <!-- Collections -->
                        <div
                            class="md-layout-item md-layout md-gutter md-alignment-center-left md-small-size-50"
                        >
                            <div class="md-layout-item md-size-50">
                                <md-button
                                    class="md-raised md-primary"
                                    @click="startCollectionSelection"
                                    :disabled="
                                        !collectionsAvailable ||
                                            this.form.bedfileIDs.length === 0 || !this.preprocessingMapLoaded
                                    "
                                    >Select Collections</md-button
                                >
                            </div>
                            <div class="md-layout-item md-size-50">
                                <span class="md-body-1"
                                    >{{ numberCollections }} collections
                                    selected</span
                                >
                            </div>
                            <div class="md-layout-item md-size-50">
                                <span
                                    style="color: red; "
                                    v-if="
                                        !$v.form.collectionIDs.required &&
                                            $v.form.collectionIDs.$dirty
                                    "
                                    >At least one collection is required</span
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
                        class="
                            md-dense
                            md-raised
                            md-primary
                            md-icon-button
                            md-alignment-horizontal-left
                        "
                        @click="
                            fetchDatasets();
                            fetchCollections();
                        "
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
import EventBus from "../../eventBus";

export default {
    name: "PreprocessCollectionForm",
    mixins: [validationMixin, apiMixin, formattingMixin],
    data: () => ({
        availableCollections: [],
        availableBedFiles: [],
        finishedCollections: [],
        processingCollections: [],
        failedCollections: [],
        form: {
            collectionIDs: [],
            bedfileIDs: []
        },
        datasetSaved: false,
        sending: false,
        preprocessingMapLoaded: false
    }),
    computed: {
        numberCollections: function(){
            return this.form.collectionIDs.length
        },
        collectionsAvailable: function() {
            return this.availableCollections.length != 0;
        },
        bedFilesAvailable: function() {
            return this.availableBedFiles.length != 0;
        },
        regionIDs: function() {
            return this.availableBedFiles.map(el => el.id);
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
            collectionIDs: {
                required
            },
            bedfileIDs: {
                required
            }
        }
    },
    methods: {
        fetchPreprocessData: function(regionID){
            // get availability object
            return this.fetchData(`datasets/${regionID}/processedDataMap/`)
        },
        getBedFileName: function(id) {
            return this.availableBedFiles.filter(el => el.id === id)[0]
                .dataset_name;
        },
        startRegionSelection: function() {
            this.expectSelection = true;
            let preselection = [...this.form.bedfileIDs];
            EventBus.$emit(
                "show-select-dialog",
                this.availableBedFiles,
                "bedfile",
                preselection,
                true
            );
        },
        startCollectionSelection: function() {
            this.expectSelection = true;
            let preselection = [...this.form.collectionIDs];
            EventBus.$emit(
                "show-select-collection-dialog",
                this.availableCollections,
                undefined,
                preselection,
                false,
                this.selectedAssembly,
                this.finishedCollections,
                this.processingCollections,
                this.failedCollections
            );
        },
        registerSelectionEventHandlers: function() {
            EventBus.$on("dataset-selected", this.handleRegionSelection);
            EventBus.$on("collection-selected", this.handleCollectionSelection);
            EventBus.$on("selection-aborted", this.hanldeSelectionAbortion);
        },
        removeSelectionEventHandlers: function() {
            EventBus.$off("dataset-selected", this.handleRegionSelection);
            EventBus.$on("collection-selected", this.handleCollectionSelection);
            EventBus.$off("selection-aborted", this.hanldeSelectionAbortion);
        },
        handleCollectionSelection: function(ids){
            if (this.expectSelection){
                this.form.collectionIDs = ids
                this.expectSelection = false
            }
        },
        handleRegionSelection: function(ids) {
            if (this.expectSelection) {
                // blank features
                this.form.collectionIDs = [];
                // blank preprocessing map loaded
                this.preprocessingMapLoaded = false
                this.form.bedfileIDs = [ids];
                // get preprocess dataset map
                this.fetchPreprocessData(ids).then(response => {
                    let lolaIDs = Object.keys(
                        response.data["lola"]
                    ).map(el => Number(el));
                    let embeddingIDs = Object.keys(
                        response.data["embedding"]
                    ).map(el => Number(el));
                    let collectiveIDs = lolaIDs.concat(embeddingIDs);
                    this.finishedCollections = this.finishedCollections.concat(
                        collectiveIDs
                    );
                    this.preprocessingMapLoaded = true
                });
                // set processing datasets and failed datasets
                this.processingCollections = this.getBedDataset(
                    ids
                ).processing_collections;
                this.failedCollections = this.getBedDataset(
                    ids
                ).failed_collections;
                this.expectSelection = false;
            }
        },
        hanldeSelectionAbortion: function() {
            this.expectSelection = false;
        },
        getBedDataset: function(id) {
            return this.availableBedFiles.filter(el => el.id === id)[0];
        },
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
        fetchCollections: function() {
            this.fetchData("collections/").then(response => {
                // update bedfiles
                this.availableCollections = response.data;
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
            this.postData("preprocess/collections/", formData).then(
                response => {
                    if (response) {
                        this.datasetSaved = true;
                    }
                    this.sending = false;
                    this.clearForm();
                }
            );
        },
        prepare_form_data() {
            // put data into form
            var form_data = {};
            form_data["collection_ids"] = JSON.stringify(this.form["collectionIDs"]);
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
        this.fetchCollections();
        this.registerSelectionEventHandlers();
    },
    beforeDestroy: function() {
        this.removeSelectionEventHandlers();
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
