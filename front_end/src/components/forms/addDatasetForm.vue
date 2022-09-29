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
                                <md-field>
                                    <!-- TODO sprint9 :class=validationClass -->
                                    <label for="fileSource">File Source</label>
                                    <md-select
                                        id="fileSource"
                                        name="fileSource"
                                        v-model="form.fileSource"
                                        @md-selected="clearInputFields"
                                        required
                                    >
                                        <md-option value="httpUpload">
                                            Upload file from device
                                        </md-option>
                                        <md-option value="url">
                                            Import from URL
                                        </md-option>
                                        <md-option
                                            v-for="repo in repositories"
                                            :key="repo.id"
                                            :value="repo.name"
                                        >
                                            {{ repo.name }}
                                        </md-option>
                                    </md-select>
                                </md-field>
                            </div>
                        </div>
                        <!-- choose upload type based on file source -->
                        <!-- file field -->
                        <div class="md-layout-item md-small-size-100">
                            <formFileInput
                                v-if="form.fileSource === 'httpUpload'"
                                :fileTypeMapping="fileTypeMapping"
                                @input-changed="fileInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <formURLInput
                                v-else-if="form.fileSource === 'url'"
                                :fileTypeMapping="fileTypeMapping"
                                @input-changed="urlInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <formRepositoryInput
                                v-else
                                :fileTypeMapping="fileTypeMapping"
                                :repository="repositories[form.fileSource].name"
                                @input-changed="repositoryInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                        </div>
                    </div>
                    <!-- metadata -->
                    <div v-if="componentValid">
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
            <md-snackbar :md-active.sync="datasetSaved">{{
                snackbarMessage
            }}</md-snackbar>
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import {
    required,
    minLength,
    maxLength,
    requiredIf,
    url
} from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

import formFileInput from "./formFileInput";
import formURLInput from "./formURLInput";
import formRepositoryInput from "./formRepositoryInput";

export default {
    name: "AddDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        fileTypeMapping: Object
    },
    components: {
        formFileInput,
        formRepositoryInput,
        formURLInput
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
            fileSource: "httpUpload"
        },
        datasetMetadataMapping: null,
        datasetSaved: false,
        sending: false,
        selectedFile: null,
        sourceURL: null,
        fileType: null,
        assemblies: {},
        repositories: {}, // TODO sprint9
        metadata: null,
        sampleID: null,
        sourceURL: null,
        fileType: null,
        selectedFile: null,
        componentValid: false,
        snackbarMessage: null
    }),
    validations() {
        // validators for the form
        let outputObject = {
            form: {
                datasetName: {
                    required,
                    minLength: minLength(3)
                },
                public: {},
                assembly: {
                    required
                },
                ValueType: {
                    required
                },
                cellCycleStage: {
                    required
                },
                perturbation: {
                    required
                },
                description: {
                    maxLength: maxLength(80)
                }
            }
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
        selectedFileType: function() {
            if (
                this.fileType &&
                this.fileType.toLowerCase() in this.fileTypeMapping
            ) {
                return this.fileTypeMapping[this.fileType.toLowerCase()];
            } else {
                return undefined;
            }
        },
        valueTypeFields: function() {
            if (this.valueTypeSelected && this.selectedFileType) {
                return Object.keys(
                    this.datasetMetadataMapping[this.selectedFileType][
                        "ValueType"
                    ][this.form.ValueType]
                );
            }
            return [];
        },
        fieldOptions: function() {
            if (this.valueTypeSelected && this.selectedFileType) {
                return this.datasetMetadataMapping[this.selectedFileType][
                    "ValueType"
                ][this.form.ValueType];
            }
            return undefined;
        },
        valueTypeSelected: function() {
            if (this.form.ValueType && this.selectedFileType) {
                return true;
            }
            return false;
        },
        valueTypes: function() {
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
        }
    },
    methods: {
        updateComponentValidity: function(validity) {
            this.componentValid = validity;
        },
        fileInputChanged: function(file, fileType) {
            this.selectedFile = file;
            this.fileType = fileType;
        },
        urlInputChanged: function(url, fileType) {
            this.sourceURL = url;
            this.fileType = fileType;
        },
        repositoryInputChanged: function(sampleID, fileType, metadata) {
            this.sampleID = sampleID;
            this.fileType = fileType;
            this.metadata = metadata;

            // fillFields
            this.form.datasetName =
                metadata["json"]["track_and_facet_info"]["dataset"];
            this.form.description =
                metadata["json"]["track_and_facet_info"]["condition"];
            // if (metadata['json']['genome_assembly'] in
        },
        fillFields: function() {
            // ... TODO fill fields with metadata
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
            for (let key of Object.keys(this.form)) {
                if (key == "public") {
                    this.form[key] = true;
                } else {
                    this.form[key] = null;
                }
            }
        },
        clearInputFields(event) {
            // TODO sprint9
            // clear fields
            this.componentValid = false;
            this.fileType = null;
            this.selectedFile = null;
            this.sampleID = null;
            this.sourceURL = null;
            this.selectedFile = null;
        },
        fetchDatasets() {
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                if (response) {
                    this.$store.commit("setDatasets", response.data);
                }
            });
        },
        saveDataset() {
            this.sending = true; // show progress bar

            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                // do not contain fileSource value, as this is only for gui
                if (key == "fileSource") {
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

            var postRoute = "";
            if (this.form.fileSource == "httpUpload") {
                formData.append(
                    "file",
                    this.selectedFile,
                    this.selectedFile.name
                );
                postRoute = "datasets/";
                this.snackbarMessage =
                    "The Dataset was added successfully and is ready for preprocessing!";
            } else if (this.form.fileSource == "url") {
                formData.append("sourceURL", this.sourceURL);
                this.snackbarMessage =
                    "The Dataset has been queued for download!";
                postRoute = "datasets/URL/";
            } else {
                formData.append("repositoryName", this.form.fileSource);
                formData.append("sampleID", this.sampleID);
                this.snackbarMessage =
                    "The Dataset has been queued for download!";
                postRoute = "datasets/encode/";
            }

            // API call including upload is made in the background
            this.postData(postRoute, formData).then(response => {
                this.sending = false;
                // this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                    this.fetchDatasets();
                }
            });
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid && this.componentValid) {
                this.saveDataset();
            }
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then(response => {
                if (response) {
                    this.assemblies = response.data;
                }
            });
        },
        fetchRepositories() {
            this.fetchData("repositories/").then(response => {
                if (response) {
                    this.repositories = response.data;
                }
            });
        }
    },
    mounted: function() {
        this.datasetMetadataMapping = this.$store.getters[
            "getDatasetMetadataMapping"
        ]["DatasetType"];
        this.assemblies = this.fetchAssemblies();

        // TODO sprint9 add repo list
        this.repositories = this.fetchRepositories();
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
