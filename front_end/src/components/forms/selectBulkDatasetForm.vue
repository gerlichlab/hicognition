<template>
    <div>
        <form
            novalidate
            class="md-layout"
            @submit.prevent="validateDataset"
            enctype="multipart/form-data"
        >
            <md-card class="md-layout-item">
                <md-card-content>
                    <div class="md-layout md-gutter">
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('files')">
                                <label for="files">Select Files</label>
                                <md-file
                                    id="files"
                                    name="files"
                                    v-model="form.files"
                                    :disabled="sending"
                                    @change="handleFileChange"
                                    required
                                    multiple
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.files.required"
                                    >Files are required</span
                                >
                                <span
                                    class="md-error"
                                    v-else-if="!$v.form.files.correctFileType"
                                >
                                    Wrong filetype!
                                </span>
                            </md-field>
                        </div>
                    </div>
                </md-card-content>
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Continue</md-button
                    >
                </md-card-actions>
            </md-card>
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";

const correctFileType = function(value) {
    /* 
        validator for correct fileype. Note that this is the vue component in this example
    */
    // string check is needed because event is first passed into the validator, followed by filename string, which is checked
    if (typeof value === "string" || value instanceof String) {
        for (let fileName of value.split(",")) {
            let splitFileName = fileName.split(".");
            let fileEnding = splitFileName[splitFileName.length - 1];
            if (!(fileEnding in this.fileTypeMapping)) {
                return false;
            }
        }
        return true;
    }
    return false;
};

export default {
    name: "selectBulkDatasetForm",
    mixins: [validationMixin],
    props: {
        fileTypeMapping: Object
    },
    data: () => ({
        form: {
            files: null
        },
        datasetSaved: false,
        sending: false,
        selectedFiles: null
    }),
    validations: {
        form: {
            files: {
                required,
                correctFiletype: correctFileType
            }
        }
    },
    methods: {
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
            // get file IO-streams
            this.selectedFiles = event.target.files;
        },
        clearForm() {
            this.$v.$reset();
            this.form.files = null;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // emit files
            this.$emit("files-selected", this.selectedFiles);
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
