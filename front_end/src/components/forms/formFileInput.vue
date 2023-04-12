<template>
    <b-form-group
      :state="getValidationState('file')"
      label="File"
      label-for="file"
      invalid-feedback="A file is required."
    >
      <b-form-file
        id="file"
        name="file"
        v-model="form.file"
        @change="handleFileChange"
        :accept="acceptedFileTypes"
        required
      ></b-form-file>
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
        getValidationState(fieldName) {
            // assigns validation state to form fields
            const field = this.$v.form[fieldName];
            if (field) {
                return (field.$invalid && field.$dirty) ? false: null
            }
            return null;
        },
    },
    computed: {
        acceptedFileTypes: function() {
            // TODO sprint9
            // build accept parameter for file chooser, e.g. ".bed,.mcool,.bw"
            return "." + Object.keys(this.fileTypeMapping).join(",.");
        }
    }
};
</script>
