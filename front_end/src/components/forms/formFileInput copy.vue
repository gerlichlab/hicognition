<template>
    <div class="md-layout-item md-layout md-gutter">
        <div class="md-layout-item md-small-size-100">
            <md-field :class="getValidationClass('file')">
                <!--:class="getValidationClass('file')">-->
                <label for="file">File</label>
                <md-file
                    id="file"
                    name="file"
                    v-model="form.file"
                    @md-change="handleFileChange"
                    :accept="acceptedFileTypes"
                    required
                />
                <span class="md-error" v-if="!$v.form.file.required"
                    >A file is required</span
                >
                <span class="md-error" v-else-if="!$v.form.file.validateFiletype">
                    Wrong filetype!
                </span>
            </md-field>
        </div>
        <div class="md-layout-item md-small-size-100">
            <md-field :class="getValidationClass('sample_id')">
                <label for="sample_id">Sample ID</label>
                <md-input
                    name="sample_id"
                    id="sample_id"
                    v-model="form.sample_id"
                    maxlength="128"
                    required
                />
                <span class="md-error" v-if="!$v.form.sample_id.required"
                    >Sample ID required!</span
                >
            </md-field>
        </div>

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

export default {
    name: "formFileInput",
    props: ["fileTypeMapping"],
    emits: ["input-changed", "update-component-validity"],
    mixins: [validationMixin],
    data: () => ({
        form: {
            file: null
        },
        componentValid: false
    }),
    validations() {
        let outputObject = {
            form: {
                file: {
                    required,
                    validFiletype: this.validFiletype
                },
                sample_id: {
                    required,
                }
            }
        };
        return outputObject;
    },
    methods: {
        validFiletype(event) {
            if (event.target) {
                event = event.target.files[0].name;
            }

            if (!(typeof event === "string" || event instanceof String)) {
                return false;
            }

            var namearray = event.split(".");
            let fileEnding = namearray[namearray.length - 1];
            return fileEnding in this.fileTypeMapping;
        },
        handleFileChange(event) {
            // check validity of form
            this.$v.$touch();
            if (!this.$v.$dirty) {
                // should not be dirty, as this method called on change anyway
                return;
            }

            // emit validity value
            this.componentValid = this.$v.$dirty && !this.$v.$invalid;
            this.$emit("update-component-validity", this.componentValid);
            console.log("update-component-validity, " + this.componentValid);

            if (!this.componentValid) {
                return;
            }

            // emit file + extension
            var nameSplit = event[0]["name"].split(".");
            this.fileExt = nameSplit[nameSplit.length - 1];
            this.$emit("input-changed", event[0], this.fileExt);
            console.log("input-changed, " + event[0] + ", " + this.fileExt);
        },
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.form[fieldName];
            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty
                };
            }
        }
    },
    computed: {
        acceptedFileTypes: function() {
            // TODO sprint9
            // build accept parameter for file chooser, e.g. ".bed,.mcool,.bw"
            return "." + Object.keys(this.fileTypeMapping).join(",.");
        },
        validationClass: function() {
            return { "md-invalid": this.$v.$dirty && this.$v.$invalid };
        }
    }
};
</script>
