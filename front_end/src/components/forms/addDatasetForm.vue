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
                        <div class="md-layout-item md-layout md-gutter">
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
                            <!-- Size Type -->
                            <div v-if="datasetType=='region'" class="md-layout-item md-small-size-100">
                                <md-field :class="getValidationClass('sizeType')">
                                    <label for="sizeType">SizeType</label>
                                    <md-select
                                        name="sizeType"
                                        id="sizeType"
                                        v-model="form.sizeType"
                                        :disabled="sending"
                                    >
                                        <md-option value="Point">Point</md-option>
                                        <md-option value="Interval">Interval</md-option>
                                    </md-select>
                                    <span
                                        class="md-error"
                                        v-if="!$v.form.sizeType.required"
                                        >A size type is required for regions</span
                                    >
                                </md-field>
                            </div>
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
                                        @md-selected="fileSourceChanged"
                                        required
                                    >
                                        <md-option value="httpUpload">
                                            Upload file from device
                                        </md-option>
                                        <md-option value="url">
                                            Import from URL
                                        </md-option>
                                        <md-option value="encode">
                                            ENCODE
                                        </md-option>
                                        <md-option
                                            v-for="repo in repositories"
                                            :key="repo.id"
                                            
                                            :value="repo.name"
                                        >
                                            {{ "4D Nucleome" }}
                                        </md-option>
                                    </md-select>
                                </md-field>
                            </div>
                        </div>
                        <!-- #TODO fix nicer the repo name -->
                        <!-- choose upload type based on file source -->
                        <!-- file field -->
                        <div class="md-layout-item md-small-size-100">
                            <formFileInput
                                v-if="form.fileSource === 'httpUpload'"
                                :fileTypeMapping="fileTypeExtensions"
                                @input-changed="fileInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <formURLInput
                                v-else-if="form.fileSource === 'url'"
                                :fileTypeMapping="fileTypeExtensions"
                                @input-changed="urlInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <formURLEncode
                                v-else-if="form.fileSource === 'encode'"
                                :fileTypeMapping="fileTypeExtensions"
                                @input-changed="urlInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <formRepositoryInput
                                v-else
                                :fileTypeMapping="fileTypeExtensions"
                                :repository="repositories[form.fileSource]['name']"
                                @input-changed="repositoryInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                        </div>
                    </div>
                    <!-- perturbation -->
                    <div class="md-layout md-gutter">
                        <div class="md-layout-item md-small-size-50">
                            <md-field>
                                    <label for="perturbation">Perturbation</label>
                                    <md-input
                                        name="perturbation"
                                        id="perturbation"
                                        v-model="form.perturbation"
                                        :disabled="sending"
                                        maxlength="30"
                                    />
                            </md-field>
                        </div>
                        <!-- celltype -->
                        <div class="md-layout-item md-small-size-50">
                            <md-field>
                                    <label for="celltype">Cell type</label>
                                    <md-input
                                        name="celltype"
                                        id="celltype"
                                        v-model="form.cellType"
                                        :disabled="sending"
                                        maxlength="30"
                                    />
                            </md-field>
                        </div>
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
    requiredIf,
    minLength,
    maxLength,
} from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

import formFileInput from "./formFileInput";
import formURLInput from "./formURLInput";
import formURLEncode from "./formURLEncode";
import formRepositoryInput from "./formRepositoryInput";

export default {
    name: "AddDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        datasetType: String,
    },
    components: {
        formFileInput,
        formRepositoryInput,
        formURLInput,
        formURLEncode
    },
    data: () => ({
        form: {
            datasetName: null,
            public: true,
            assembly: null,
            sizeType: null,
            file: null,
            description: null,
            perturbation: null,
            cellType: null,
            fileSource: "httpUpload"
        },
        fileTypes: null,
        datasetSaved: false,
        sending: false,
        selectedFile: null,
        sourceURL: null,
        assemblies: {},
        repositories: {}, // TODO sprint9
        repositoryMetadata: null,
        sampleID: null,
        sourceURL: null,
        fileExt: null,
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
                cellType: {},
                perturbation: {},
                assembly: {
                    required
                },
                description: {
                    maxLength: maxLength(80)
                },
                sizeType: {
                    required: requiredIf(function() {
                        return this.datasetType == 'region'
                    })
                }
            }
        };
        return outputObject;
    },
    computed: {
        selectedFileType: function() {
            if (
                this.fileExt &&
                this.fileExt.toLowerCase() in this.fileTypeExtensions
            ) {
                return this.fileTypeExtensions[this.fileExt.toLowerCase()];
            } else {
                return undefined;
            }
        }
    },
    methods: {
        updateComponentValidity: function(validity) {
            this.componentValid = validity;
        },
        fileInputChanged: function(file, fileExt) {
            this.selectedFile = file;
            this.fileExt = fileExt;
        },
        urlInputChanged: function(url, fileExt) {
            this.sourceURL = url;
            this.fileExt = fileExt;
        },
        repositoryInputChanged: function(sampleID, fileExt, repositoryMetadata) {
            this.sampleID = sampleID;
            this.fileExt = fileExt;
            this.repositoryMetadata = repositoryMetadata;

            // fillFields
            this.form.datasetName =
                repositoryMetadata["json"]["track_and_facet_info"]["dataset"];
            this.form.description =
                repositoryMetadata["json"]["track_and_facet_info"]["condition"];
            // if (metadata['json']['genome_assembly'] in
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
            this.form.fileSource = 'httpUpload';
        },
        fileSourceChanged(event) {
            // clear fields
            this.componentValid = false;
            this.fileExt = null;
            this.selectedFile = null;
            this.sampleID = null;
            this.sourceURL = null;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            //formData.append('dataset_type', this.datasetType);
            formData.append('dataset_name', this.form['datasetName']);
            formData.append('public', this.form['public']);
            formData.append('assembly', this.form['assembly']);
            if (this.datasetType == 'region') {
                formData.append("sizeType", this.form["sizeType"]);
            }
            formData.append('description', this.form['description']);
            formData.append('perturbation', this.form['perturbation']);
            formData.append('cellType', this.form['cellType']);
            formData.append("filetype", this.selectedFileType);

            // Differentiate depending on chosen file source
            var postRoute = "";
            if (this.form.fileSource == "httpUpload") {
                formData.append("file",this.selectedFile,this.selectedFile.name);
                postRoute = "datasets/";
                this.snackbarMessage =
                    "The Dataset was added successfully and is ready for preprocessing!";
            } else if (this.form.fileSource == "url") {
                formData.append("source_url", this.sourceURL);
                this.snackbarMessage = "The Dataset has been queued for download!";
                postRoute = "datasets/URL/";
            } else {
                formData.append("repository_name", this.form.fileSource);
                formData.append("sample_id", this.sampleID);
                this.snackbarMessage = "The Dataset has been queued for download!";
                postRoute = "datasets/encode/";
            }

            // API call including upload is made in the background
            this.postData(postRoute, formData).then((response) => {
                this.sending = false;
                this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                    this.fetchAndStoreDatasets(); // apiMixin
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
    created: function() {
        this.assemblies = this.fetchAssemblies();

        // TODO sprint9 add repo list
        this.repositories = this.fetchRepositories();

        var fileTypes = this.$store.getters["getFileTypes"];
        this.fileTypes = {};
        this.fileTypeExtensions = {};

        Object.entries(fileTypes).forEach(([name, fileType]) => {
            // check if region or feature accept data type
            if (fileType['dataset_type'].includes(this.datasetType)) { 
                this.fileTypes[name] = fileType;
                fileType['file_ext'].forEach(ext => {
                    this.fileTypeExtensions[ext] = name;
                });
            }
        });
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
