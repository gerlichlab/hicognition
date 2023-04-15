<template>
        <b-overlay :show="sending">
            <b-card>
                <b-card-body>
                    <b-row>
                        <b-col cols="4">
                            <b-form-group
                                :state="getValidationState('datasetName')"
                                label="Name"
                                label-for="dataset-name"
                            >
                                <b-form-input
                                    id="dataset-name"
                                    v-model="form.datasetName"
                                    :state="getValidationState('datasetName')"
                                    :disabled="sending"
                                    maxlength="30"
                                    required
                                ></b-form-input>
                                    <b-form-invalid-feedback v-if="!$v.form.datasetName.required">
                                    A dataset name is required
                                    </b-form-invalid-feedback>
                                    <b-form-invalid-feedback v-else-if="!$v.form.datasetName.minlength">
                                    Invalid dataset name
                                    </b-form-invalid-feedback>
                            </b-form-group>
                        </b-col>

                        <b-col cols="4">
                            <b-form-group
                                :state="getValidationState('assembly')"
                                label="Genome assembly"
                                label-for="assembly"
                            >
                                <b-form-select
                                    id="assembly"
                                    v-model="form.assembly"
                                    :state="getValidationState('assembly')"
                                    :disabled="sending"
                                >
                                    <b-form-select-option-group
                                        v-for="(values, org) in assemblies"
                                        :key="org"
                                        :label="org"
                                    >
                                        <b-form-select-option
                                            v-for="assembly in values"
                                            :key="assembly.id"
                                            :value="assembly.id"
                                        >
                                            {{ assembly.name }}
                                        </b-form-select-option>
                                    </b-form-select-option-group>
                                </b-form-select>
                                <b-form-invalid-feedback
                                    v-if="!$v.form.assembly.required"
                                >
                                    A genome assembly is required
                                </b-form-invalid-feedback>
                            </b-form-group>
                        </b-col>

                        <b-col v-if="datasetType == 'region'" cols="4">
                            <b-form-group
                                :state="getValidationState('sizeType')"
                                label="SizeType"
                                label-for="sizeType"
                            >
                                <b-form-select
                                    id="sizeType"
                                    v-model="form.sizeType"
                                    :state="getValidationState('sizeType')"
                                    :disabled="sending"
                                >
                                    <b-form-select-option value="Point"
                                        >Point</b-form-select-option
                                    >
                                    <b-form-select-option value="Interval"
                                        >Interval</b-form-select-option
                                    >
                                </b-form-select>
                                <b-form-invalid-feedback
                                    v-if="!$v.form.sizeType.required"
                                >
                                    A size type is required for regions
                                </b-form-invalid-feedback>
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-row>
                        <b-col cols="2">
                            <b-form-group>
                                <b-form-checkbox
                                    v-model="form.public"
                                    false-value="false"
                                >
                                    Public
                                </b-form-checkbox>
                            </b-form-group>
                        </b-col>

                        <b-col cols="4">
                            <b-form-group
                                label="File Source"
                                label-for="fileSource"
                            >
                                <b-form-select
                                    id="fileSource"
                                    v-model="form.fileSource"
                                    @change="fileSourceChanged"
                                    required
                                >
                                    <b-form-select-option value="httpUpload">
                                        Upload file from device
                                    </b-form-select-option>
                                    <b-form-select-option value="url">
                                        Import from URL
                                    </b-form-select-option>
                                    <b-form-select-option value="url">
                                        ENCODE
                                    </b-form-select-option>
                                    <b-form-select-option
                                        v-for="repo in repositories"
                                        :key="repo.id"
                                        :value="repo.name"
                                    >
                                        4D Nucleome
                                    </b-form-select-option>
                                </b-form-select>
                            </b-form-group>
                        </b-col>

                        <b-col cols="6">
                            <form-file-input
                                v-if="form.fileSource === 'httpUpload'"
                                :file-type-mapping="fileTypeExtensions"
                                @input-changed="fileInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <form-url-input
                                v-else-if="form.fileSource === 'url'"
                                :file-type-mapping="fileTypeExtensions"
                                @input-changed="urlInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                            <form-repository-input
                                v-else
                                :file-type-mapping="fileTypeExtensions"
                                :repository="
                                    repositories[form.fileSource]['name']
                                "
                                @input-changed="repositoryInputChanged"
                                @update-component-validity="
                                    updateComponentValidity
                                "
                            />
                        </b-col>



                    </b-row>

                    <b-row>
                        <b-col cols="12" sm="6">
                            <b-form-group
                                label="Perturbation"
                                label-for="perturbation"
                            >
                                <b-form-input
                                    id="perturbation"
                                    v-model="form.perturbation"
                                    :disabled="sending"
                                    maxlength="30"
                                ></b-form-input>
                            </b-form-group>
                        </b-col>
                        <b-col cols="12" sm="6">
                            <b-form-group
                                label="Cell type"
                                label-for="celltype"
                            >
                                <b-form-input
                                    id="celltype"
                                    v-model="form.cellType"
                                    :disabled="sending"
                                    maxlength="30"
                                ></b-form-input>
                            </b-form-group>
                        </b-col>
                    </b-row>

                    <b-form-group
                        :state="getValidationState('description')"
                        label="Short Description"
                        label-for="description"
                    >
                        <b-form-textarea
                            id="description"
                            v-model="form.description"
                            :state="getValidationState('description')"
                            :disabled="sending"
                            maxlength="80"
                            rows="3"
                            max-rows="6"
                        ></b-form-textarea>
                    </b-form-group>
                </b-card-body>
            </b-card>
        </b-overlay>
</template>

<script>
import { validationMixin } from "vuelidate";
import {
    required,
    requiredIf,
    minLength,
    maxLength
} from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

import formFileInput from "./formFileInput";
import formUrlInput from "./formURLInput";
import formRepositoryInput from "./formRepositoryInput";

export default {
    name: "AddDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        datasetType: String
    },
    components: {
        formFileInput,
        formRepositoryInput,
        formUrlInput
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
        snackbarMessage: null,
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
                        return this.datasetType == "region";
                    })
                }
            },
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
        toast(title, message) {
        this.$bvToast.toast(message, {
          title: title,
          toaster: 'b-toaster-top-right',
          solid: true,
          appendToast: true
        })
      },
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
        repositoryInputChanged: function(
            sampleID,
            fileExt,
            repositoryMetadata
        ) {
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
        getValidationState(fieldName) {
            // assigns validation state to form fields
            const field = this.$v.form[fieldName];
            if (field) {
                return (field.$invalid && field.$dirty) ? false: null
            }
            return null;
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
            this.form.fileSource = "httpUpload";
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
            formData.append("dataset_name", this.form["datasetName"]);
            formData.append("public", this.form["public"]);
            formData.append("assembly", this.form["assembly"]);
            if (this.datasetType == "region") {
                formData.append("sizeType", this.form["sizeType"]);
            }
            formData.append("description", this.form["description"]);
            formData.append("perturbation", this.form["perturbation"]);
            formData.append("cellType", this.form["cellType"]);
            formData.append("filetype", this.selectedFileType);

            // Differentiate depending on chosen file source
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
                formData.append("source_url", this.sourceURL);
                this.snackbarMessage =
                    "The Dataset has been queued for download!";
                postRoute = "datasets/URL/";
            } else {
                formData.append("repository_name", this.form.fileSource);
                formData.append("sample_id", this.sampleID);
                this.snackbarMessage =
                    "The Dataset has been queued for download!";
                postRoute = "datasets/encode/";
            }

            // API call including upload is made in the background
            this.postData(postRoute, formData).then(response => {
                this.sending = false;
                this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                    this.fetchAndStoreDatasets(); // apiMixin
                    this.toast('Success', this.snackbarMessage)
                }
                this.$emit("dataset-saved-finished")
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
            if (fileType["dataset_type"].includes(this.datasetType)) {
                this.fileTypes[name] = fileType;
                fileType["file_ext"].forEach(ext => {
                    this.fileTypeExtensions[ext] = name;
                });
            }
        });
    },
};
</script>

<style lang="scss" scoped>
.container {
  overflow: visible !important;
}
</style>
