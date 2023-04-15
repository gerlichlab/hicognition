<template>
    <b-form-group
      :state="getValidationState('file')"
      label="File"
      label-for="file"
    >
      <b-form-file
        id="file"
        name="file"
        v-model="form.file"
        :accept="acceptedFileTypes"
        :state="getValidationState('file')"
        required
      ></b-form-file>
    <b-form-invalid-feedback v-if="!$v.form.file.required">
      A file is required.
    </b-form-invalid-feedback>
    <b-form-invalid-feedback v-if="!$v.form.file.validFileType">
      Filetype is invalid.
    </b-form-invalid-feedback>
    </b-form-group>
</template>


<script>
import { validationMixin } from "vuelidate";
import {
    required
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
                }
            }
        };
        return outputObject;
    },
    methods: {
        validFiletype(event) {
            if (this.form.file) {
                event = this.form.file.name;
            }

            if (!(typeof event === "string" || event instanceof String)) {
                return false;
            }

            var namearray = event.split(".");
            let fileEnding = namearray[namearray.length - 1];
            return fileEnding in this.fileTypeMapping;
        },
        handleFileChange() {
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
            var nameSplit =this.form.file["name"].split(".");
            this.fileExt = nameSplit[nameSplit.length - 1];
            this.$emit("input-changed", this.form.file, this.fileExt);
            console.log("input-changed, " + this.form.file + ", " + this.fileExt);
        },
        getValidationState() {
            // assigns validation state to form fields
            return (this.$v.$invalid && this.$v.$dirty) ? false: null
        },
    },
    computed: {
        acceptedFileTypes: function() {
            // TODO sprint9
            // build accept parameter for file chooser, e.g. ".bed,.mcool,.bw"
            return "." + Object.keys(this.fileTypeMapping).join(",.");
        }
    },
    watch: {
        "form.file": {
            handler: function() {
                // this is needed because the change event of the input field is not triggered before form.file updates
                this.handleFileChange();
            },
            deep: true
        }
    }
};
</script>
