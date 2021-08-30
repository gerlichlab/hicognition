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
                            <md-field
                                :class="getValidationClass('datasetName')"
                            >
                                <label for="dataset-name">Name</label>
                                <md-input
                                    name="dataset-name"
                                    id="dataset-name"
                                    v-model="form.datasetName"
                                    :disabled="sending"
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
                        <!-- public checkbox -->
                        <div class="md-layout-item md-small-size-100">
                            <md-checkbox
                                v-model="form.public"
                                class="top-margin"
                                >Public</md-checkbox
                            >
                        </div>
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
                                <span
                                    class="md-error"
                                    v-else-if="!$v.form.file.correctFileType"
                                >
                                    Wrong filetype!
                                </span>
                            </md-field>
                        </div>
                    </div>
                    <!-- metadata -->
                    <div v-if="showMetadata">
                        <md-divider />
                        <md-list>
                            <md-subheader>Metadata</md-subheader>
                            <md-list-item>
                                <div class="md-layout md-gutter">
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="getValidationClass('valueType')"
                                        >
                                            <label for="valueType"
                                                >Value Type</label
                                            >
                                            <md-select
                                                name="valueType"
                                                id="valueType"
                                                v-model="form.valueType"
                                                :disabled="sending"
                                            >
                                                <md-option
                                                    v-for="valueType in valueTypes"
                                                    :key="valueType"
                                                    >{{ valueType }}</md-option
                                                >
                                            </md-select>
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.valueType
                                                        .required
                                                "
                                                >A ValueType is
                                                required</span
                                            >
                                        </md-field>
                                    </div>
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field>
                                            <label for="valueType"
                                                >Method</label
                                            >
                                            <md-select
                                                name="valueType"
                                                id="valueType"
                                                :disabled="
                                                    sending ||
                                                    !valueTypeSelected
                                                "
                                            >
                                                <md-option
                                                    v-for="valueType in valueTypes"
                                                    :key="valueType"
                                                    >{{ valueType }}</md-option
                                                >
                                            </md-select>
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
import { required, minLength, maxLength } from "vuelidate/lib/validators";
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
            public: false,
            assembly: null,
            file: null,
            description: null,
            valueType: null,
        },
        datasetMetadataMapping: null,
        datasetSaved: false,
        sending: false,
        selectedFile: null,
        assemblies: {},
    }),
    validations: {
        // validators for the form
        form: {
            datasetName: {
                required,
                minLength: minLength(3),
            },
            public: {},
            assembly: {
                required,
            },
            valueType: {
                required,
            },
            file: {
                required,
                correctFiletype: correctFileType,
            },
            description: {
                maxLength: maxLength(80),
            },
        },
    },
    computed: {
        valueTypeSelected: function () {
            return false;
        },
        valueTypes: function () {
            if (this.fileEnding) {
                return Object.keys(
                    this.datasetMetadataMapping[this.selectedFileType][
                        "ValueType"
                    ]
                );
            }
            return undefined;
        },
        showMetadata: function () {
            // whether to show metadata fields
            if (this.fileEnding) {
                return true;
            }
            return false;
        },
        selectedFileType: function () {
            if (this.fileEnding) {
                return this.fileTypeMapping[this.fileEnding.toLowerCase()];
            }
            return undefined;
        },
        fileEnding: function () {
            if (
                typeof this.form.file === "string" ||
                this.form.file instanceof String
            ) {
                var splitFileName = this.form.file.split(".");
                return splitFileName[splitFileName.length - 1];
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
        handleFileChange(event) {
            // get file IO-stream
            this.selectedFile = event.target.files[0];
        },
        clearForm() {
            this.$v.$reset();
            this.form.datasetName = null;
            this.form.assembly = null;
            this.form.file = null;
            this.form.description = null;
            this.form.public = false;
            this.form.valueType = null;
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
            // add filetype
            formData.append("filetype", this.selectedFileType);
            // API call including upload is made in the background
            this.postData("datasets/", formData).then((response) => {
                this.sending = false;
                this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                }
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
                    this.assemblies = response.data;
                }
            });
        },
    },
    mounted: function () {
        this.datasetMetadataMapping =
            this.$store.getters["getDatasetMetadataMapping"]["DatasetType"];
        this.assemblies = this.fetchAssemblies();
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
