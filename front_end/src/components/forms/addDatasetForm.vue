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
                    <!-- Dataset name and genotyp; first row -->
                    <div class="md-layout md-gutter">
                        <!-- dataset name -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field
                                :class="getValidationClass('datasetName')"
                            >
                                <label for="dataset-name">Name</label>
                                <md-input
                                    name="dataset-name"
                                    id="dataset-name"
                                    v-model="form.datasetName"
                                    :disabled="sending"
                                    maxlength="30"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.datasetName.required"
                                    >A dataset name is required</span
                                >
                                <span
                                    class="md-error"
                                    v-else-if="!$v.form.datasetName.minlength"
                                    >Invalid dataset name</span
                                >
                            </md-field>
                        </div>
                        <!-- Genotype field -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('assembly')">
                                <label for="assembly">Genome assembly</label>
                                <md-select
                                    name="assembly"
                                    id="assembly"
                                    v-model="form.assembly"
                                    :disabled="sending"
                                >
                                    <md-optgroup
                                        v-for="(values, org) in assemblies"
                                        :key="org"
                                        :label="org"
                                    >
                                        <md-option
                                            v-for="assembly in values"
                                            :key="assembly.id"
                                            :value="assembly.id"
                                            >{{ assembly.name }}</md-option
                                        >
                                    </md-optgroup>
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.assembly.required"
                                    >A genome assembly is required</span
                                >
                            </md-field>
                        </div>
                    </div>

                    <!-- Second row -->
                    <div class="md-layout md-gutter">
                        <div class="md-layout-item md-layout md-gutter">
                            <!-- public checkbox -->
                            <div class="md-layout-item md-small-size-100">
                                <md-checkbox
                                    v-model="form.public"
                                    false-value="false"
                                    class="top-margin"
                                    >Public</md-checkbox
                                >
                            </div>
                            <!-- select file source -->
                            <div class="md-layout-item md-small-size-100">
                                <md-field> <!-- TODO sprint9 :class=validationClass -->
                                    <label for="fileSource">File Source</label>
                                    <md-select
                                        id="fileSource"
                                        name="fileSource"
                                        v-model="form.fileSource"
                                        @md-selected="clearFileFields"
                                        required
                                    >
                                        <md-option value="httpUpload"> 
                                            Upload file from device
                                        </md-option>
                                        <md-option value="url"> 
                                            Import from URL
                                        </md-option>
                                        <md-option v-for="repo in repositories"
                                            :key="repo.id"
                                            :value="repo.name">
                                            {{repo.name}}
                                        </md-option>
                                    </md-select>
                                </md-field>
                            </div>
                        </div>
                        <!-- choose upload type based on file source -->
                        <!-- file field -->
                        <div v-if="form.fileSource==='httpUpload'" class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('file')">
                                <label for="file">File</label>
                                <md-file
                                    id="file"
                                    name="file"
                                    v-model="form.file"
                                    :disabled="sending"
                                    @change="handleFileChange"
                                    :accept="acceptedFileTypes"
                                />
                                    <!-- required -->
                                <span
                                    class="md-error"
                                    v-if="!$v.form.file.required"
                                    >A file is required</span
                                >
                                <span
                                    class="md-error"
                                    v-else-if="!$v.form.file.correctFileType"
                                >
                                    Wrong filetype! 
                                </span>
                            </md-field>
                        </div>
                        <!-- URL -->
                        <div v-else-if="form.fileSource==='url'" class="md-layout-item md-layout md-gutter">
                            <div class="md-layout-item md-small-size-100"> 
                                <md-field :class="getValidationClass('sourceURL')">
                                    <label for="sourceURL">URL</label>
                                    <md-input
                                        name="sourceURL"
                                        id="sourceURL"
                                        v-model="form.sourceURL"
                                        :disabled="sending"
                                        
                                    /><!-- url -->
                                        <!-- required -->
                                    <span
                                        class="md-error"
                                        v-if="!$v.form.sourceURL.url"
                                        >Please check if URL is valid</span
                                    >
                                    <!-- <span
                                        class="md-error"
                                        v-if="!$v.form.sourceURL.required"
                                        >URL required</span
                                    > -->
                                </md-field>
                            </div>
                            <div class="md-layout-item md-small-size-100">
                                <md-field :class="getValidationClass('fileType')">
                                    <label for="fileType">File type</label>
                                    <md-select
                                        id="fileType"
                                        name="fileType"
                                        v-model="form.fileType"
                                    >
                                        <!-- required -->
                                        <md-option v-for="fileType in fileTypes"
                                            :key="fileType"
                                            :value="fileType">
                                            {{fileType}}
                                        </md-option>
                                    </md-select>
                                </md-field>
                            </div>
                        </div>
                        <div v-else class="md-layout-item md-small-size-100"> 
                            <md-field :class="getValidationClass('sampleID')">
                                <label for="sampleID">Sample ID</label>
                                <md-input
                                    name="sampleID"
                                    id="sampleID"
                                    v-model="form.sampleID"
                                    :disabled="sending"
                                    @change="fetchSampleMetadata"
                                />
                                    <!-- required -->
                                <span
                                    class="md-error"
                                    v-if="!$v.form.sampleID.required"
                                    >Sample ID required</span
                                >
                                <span
                                    class="md-error"
                                    v-if="!$v.form.sampleID.notFound"
                                    >Sample not found</span
                                >
                            </md-field>
                        </div>
                    </div>
                    <!-- metadata -->
                    <div v-if="showMetadata">
                        <md-divider />
                        <md-list>
                            <md-subheader>Dataset descriptions</md-subheader>
                            <md-list-item>
                                <div class="md-layout md-gutter">
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="
                                                getValidationClass(
                                                    'perturbation'
                                                )
                                            "
                                        >
                                            <label for="perturbation"
                                                >Perturbation</label
                                            >
                                            <md-input
                                                name="perturbation"
                                                id="perturbation"
                                                v-model="form.perturbation"
                                                :disabled="sending"
                                                required
                                            />
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.perturbation
                                                        .required
                                                "
                                                >Perturbation information is
                                                required is required</span
                                            >
                                        </md-field>
                                    </div>
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="
                                                getValidationClass(
                                                    'cellCycleStage'
                                                )
                                            "
                                        >
                                            <label for="perturbation"
                                                >Cell cycle Stage</label
                                            >
                                            <md-input
                                                name="cellcycleStage"
                                                id="cellcycleStage"
                                                v-model="form.cellCycleStage"
                                                :disabled="sending"
                                                required
                                            />
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.cellCycleStage
                                                        .required
                                                "
                                                >Cell cycle stage is
                                                required</span
                                            >
                                        </md-field>
                                    </div>
                                </div>
                            </md-list-item>
                            <md-list-item>
                                <div class="md-layout md-gutter">
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="
                                                getValidationClass('valueType')
                                            "
                                        >
                                            <label for="valueType"
                                                >Value Type</label
                                            >
                                            <md-select
                                                name="valueType"
                                                id="valueType"
                                                v-model="form.ValueType"
                                                required
                                                :disabled="sending"
                                            >
                                                <md-option
                                                    v-for="valueType in valueTypes"
                                                    :key="valueType"
                                                    :value="valueType"
                                                    >{{ valueType }}</md-option
                                                >
                                            </md-select>
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.ValueType.required
                                                "
                                                >A ValueType is required</span
                                            >
                                        </md-field>
                                    </div>
                                </div>
                            </md-list-item>
                            <md-list-item>
                                <div
                                    class="md-layout md-gutter"
                                    v-if="valueTypeSelected"
                                >
                                    <div
                                        class="md-layout-item md-small-size-100"
                                        v-for="field in valueTypeFields"
                                        :key="field"
                                    >
                                        <md-field
                                            :class="getValidationClass(field)"
                                        >
                                            <label for="valueType">{{
                                                field
                                            }}</label>

                                            <md-select
                                                :name="field"
                                                :id="field"
                                                v-model="form[field]"
                                                required
                                                :disabled="sending"
                                                v-if="
                                                    fieldOptions[field] !=
                                                    'freetext'
                                                "
                                            >
                                                <md-option
                                                    v-for="option in fieldOptions[
                                                        field
                                                    ]"
                                                    :key="option"
                                                    :value="option"
                                                    >{{ option }}</md-option
                                                >
                                            </md-select>
                                            <md-input
                                                :name="field"
                                                :id="field"
                                                v-model="form[field]"
                                                :disabled="sending"
                                                required
                                                v-else
                                            />
                                            <span
                                                class="md-error"
                                                v-if="!$v.form[field].required"
                                                >{{ field }} is required</span
                                            >
                                        </md-field>
                                    </div>
                                </div>
                            </md-list-item>
                        </md-list>
                        <md-divider />
                    </div>
                    <!-- Short description field -->
                    <md-field :class="getValidationClass('description')">
                        <label for="description">Short Description</label>
                        <md-textarea
                            v-model="form.description"
                            md-counter="80"
                            maxlength="80"
                            :disabled="sending"
                        />
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
                    <md-button class="md-primary" @click="$emit('close-dialog')"
                        >Close</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >The Dataset was added successfully and is ready for
                preprocessing!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required, minLength, maxLength, requiredIf, url } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

const correctFileType = function (value) {
    /* 
        validator for correct fileype. Note that this is the vue component in this example
    */
    // string check is needed because event is first passed into the validator, followed by filename string, which is checked
    if (typeof value === "string" || value instanceof String) {
        let splitFileName = value.split(".");
        let fileEnding = splitFileName[splitFileName.length - 1];
        return fileEnding in this.fileTypeMapping;
    }
    return false;
};

export default {
    name: "AddDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        fileTypeMapping: Object,
    },
    data: () => ({
        form: {
            datasetName: null,
            public: true,
            assembly: null,
            file: null,
            description: null,
            ValueType: null,
            Normalization: null,
            Method: null,
            SizeType: null,
            Directionality: null,
            DerivationType: null,
            Protein: null,
            cellCycleStage: null,
            perturbation: null,
            fileSource: 'httpUpload', // TODO sprint9,
            sampleID: null,
            sourceURL: null,
            fileType: null,
        },
        datasetMetadataMapping: null,
        datasetSaved: false,
        sending: false,
        selectedFile: null,
        assemblies: {},
        repositories: {}, // TODO sprint9
        sample_not_foun: false,
        sampleMetadata: ''
        

    }),
    validations() {
        // validators for the form
        let outputObject = {
            form: {
                datasetName: {
                    required,
                    minLength: minLength(3),
                },
                public: {},
                assembly: {
                    required,
                },
                ValueType: {
                    required,
                },
                cellCycleStage: {
                    required,
                },
                perturbation: {
                    required,
                },
                file: { // TODO sprint9
                    correctFiletype: correctFileType, // TODO check required
                },
                sourceURL: {
                //     url, // TODO check required
                },
                sampleID: {
                //     // TODO check required
                },
                description: {
                    maxLength: maxLength(80),
                },
            },
        };
        if (this.valueTypeSelected) {
            for (let key of Object.keys(
                this.datasetMetadataMapping[this.selectedFileType]["ValueType"][
                    this.form.ValueType
                ]
            )) {
                outputObject["form"][key] = { required };
            }
        }
        return outputObject;
    },
    computed: {
        fileTypes: function() { // TODO sprint9 naming is really bad for this one
            // list of filetypes to choose from
            // only allow unique values
            let fileTypesLC = Object.keys(this.fileTypeMapping).map((type) => type.toLowerCase())
            let fileTypes = [...new Set(fileTypesLC)]
            return fileTypes
        },
        acceptedFileTypes: function() { // TODO sprint9
            // build accept parameter for file chooser, e.g. ".bed,.mcool,.bw"
            return "." + Object.keys(this.fileTypeMapping).join(',.')
        },
        valueTypeFields: function () {
            if (this.valueTypeSelected && this.selectedFileType) {
                return Object.keys(
                    this.datasetMetadataMapping[this.selectedFileType][
                        "ValueType"
                    ][this.form.ValueType]
                );
            }
            return [];
        },
        fieldOptions: function () {
            if (this.valueTypeSelected && this.selectedFileType) {
                return this.datasetMetadataMapping[this.selectedFileType][
                    "ValueType"
                ][this.form.ValueType];
            }
            return undefined;
        },
        valueTypeSelected: function () {
            if (this.form.ValueType && this.selectedFileType) {
                return true;
            }
            return false;
        },
        valueTypes: function () {
            if (this.selectedFileType) {
                let valueTypes = Object.keys(
                    this.datasetMetadataMapping[this.selectedFileType][
                        "ValueType"
                    ]
                );
                // if there is only one value type, select it
                if (valueTypes.length == 1) {
                    this.$set(this.form, "ValueType", valueTypes[0]);
                }
                return valueTypes;
            }
            return undefined;
        },
        showMetadata: function () { // REFACTOR showMetadata
            // checks if all prerequisites are fulfilled to continue filling form
            // depends on chosen file source: 
            //  user upload: is file of correct type
            //  encode repo: is id correct (have we received metadata)
            //  URL upload: is chosen fileEnding correct, URLs may end with no filetype
            // show = true;
            // if (this.form.fileSource == 'httpUpload') {

            // } else if (this.form.fileSource == 'url') {

            // } else if (this.form.fileSource != '') {
            //     show = sampleMetadata.length() > 0
            //     show = show && (sampleMetadata['accession'] == this.form.sampleID)
            // }

            if (this.selectedFileType) {
                return true;
            }
            return false;
        },
        selectedFileType: function () {
                if (this.fileEnding) {
                    if (this.fileEnding.toLowerCase() in this.fileTypeMapping) {
                        return this.fileTypeMapping[this.fileEnding.toLowerCase()];
                    }
                    // show rerror
                    this.$v.form.file.$touch();
                }
            return undefined;
        },
        // REFACTOR currently validating the script with fileEnding, selectedFileType and showMetadata
        fileEnding: function () { // TODO sprint9
            if (this.form.fileSource == 'httpUpload') {
                if (
                    typeof this.form.file === "string" ||
                    this.form.file instanceof String
                ) {
                    var splitFileName = this.form.file.split(".");
                    return splitFileName[splitFileName.length - 1];
                }
            } else if (this.form.fileSource == 'url') {
                return this.form.fileType;
            } else if (this.form.fileSource != '') {
                if (this.sampleMetadata != '' && this.sampleMetadata['accession'] == this.form.sampleID) {
                    return this.sampleMetadata['file_format']['file_format']
                }
            }
            return undefined;
        },
    },
    methods: {
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.form[fieldName];

            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty,
                };
            }
        },
        handleFileChange(event) {  // TODO sprint9
            // get file IO-stream
            this.selectedFile = event.target.files[0];
        },
        clearForm() {
            this.$v.$reset();
            for (let key of Object.keys(this.form)) {
                if (key == "public") {
                    this.form[key] = true;
                } else {
                    this.form[key] = null;
                }
            }
        },
        fetchDatasets() {
            this.fetchData("datasets/").then((response) => {
                // success, store datasets
                if (response) {
                    this.$store.commit("setDatasets", response.data);
                }
            });
        },
        saveDataset() {
            //this.sending = true; // show progress bar

            var postRoute = '';
            if (this.form.fileSource == 'httpUpload') {
                postRoute = 'datasets/';
            } else if (this.form.fileSource == 'url') {
                postRoute = 'datasets/URL';
            } else {
                postRoute = 'datasets/encode';
            }

            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                // do not contain fileSource value, as this is only for gui
                if (key == 'fileSource') {
                    continue;
                }

                // only include fields if they are not null
                if (this.form[key]) {
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
            }
            // add filetype
            formData.append("filetype", this.selectedFileType);
            // API call including upload is made in the background
            this.postData(postRoute, formData).then((response) => {
                // this.sending = false;
                // this.clearForm();
                // if (response) {
                //     // if error happend, global error handler will eat the response
                //     this.datasetSaved = true;
                //     this.fetchDatasets();
                // }
            });
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then((response) => {
                if (response) {
                    this.assemblies = response.data; // TODO ask => shouldn't return?
                }
            });
        },
        fetchRepositories() { // TODO sprint9 get repos list
            this.fetchData("repositories/").then((response) => {
                if (response) {
                    this.repositories = response.data;
                }
            });
        },
        clearFileFields(event) { // TODO sprint9
            this.form.fileType = null;
            this.form.file = null;
            this.form.sampleID = null;
            this.form.sourceURL = null;
        },
        fetchSampleMetadata: function (event) {
            // 4DNFIRCHWS8M 
            if (this.form.sampleID.length <= 3) {
                return;
            }

            var repo_name = this.repositories[this.form.fileSource].name;

            this.fetchData(`ENCODE/${repo_name}/${this.form.sampleID}/`)
                .then((response) => this.fetchSampleMetadataResponse(response.data))
                .catch((error) => this.fetchSampleMetadataError(error))
        },
        fetchSampleMetadataResponse: function (sampleMetadata) {
            if (sampleMetadata['status'] == 'error') {
                this.sampleMetadata = '';
                return;
                // TODO update gui
            } else if (sampleMetadata['status'] == 'ok') {
                this.form.datasetName = sampleMetadata['json']['track_and_facet_info']['dataset'];
                this.form.description = sampleMetadata['json']['description'];
                this.form.fileEnding = sampleMetadata['json']['file_format']['file_format'].toLowerCase();
            }
            
            // TODO how to assign metadata
        },
        fetchSampleMetadataError: function (error) {
            this.sampleMetadata = '';
            // TODO error handling
        }
    },
    mounted: function () {
        this.datasetMetadataMapping =
            this.$store.getters["getDatasetMetadataMapping"]["DatasetType"];
        this.assemblies = this.fetchAssemblies();
        
        // TODO sprint9 add repo list
        this.repositories = this.fetchRepositories();
    },
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
