<template>
  <b-form-row>
    <b-col>
      <b-form-group label="URL">
        <b-form-input
          id="sourceURL"
          v-model="form.sourceURL"
          @change="inputURLChanged"
          :state="validationSourceURL"
          required
        />
        <b-form-invalid-feedback v-if="!$v.form.sourceURL.url">
          URL invalid! {{ urlErrorMsg }}
        </b-form-invalid-feedback>
        <b-form-invalid-feedback v-if="!$v.form.sourceURL.required">
          URL required!
        </b-form-invalid-feedback>
      </b-form-group>
    </b-col>
    <b-col>
      <b-form-group label="File type">
        <b-form-select
          id="fileType"
          v-model="form.fileType"
          @change="inputFileTypeChanged"
          :state="validationFileType"
          required
        >
          <b-form-select-option disabled value="">
            Choose file type
          </b-form-select-option>
          <b-form-select-option
            v-for="fileType in fileTypes"
            :key="fileType"
            :value="fileType"
          >
            {{ fileType }}
          </b-form-select-option>
        </b-form-select>
        <b-form-invalid-feedback v-if="!$v.form.fileType.required">
          Filetype is required
        </b-form-invalid-feedback>
      </b-form-group>
    </b-col>
  </b-form-row>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required, url } from "vuelidate/lib/validators";

export default {
    name: "formURLInput",
    props: ["fileTypeMapping"],
    emits: ["input-changed", "update-component-validity"],
    mixins: [validationMixin],
    data: () => ({
        form: {
            sourceURL: null,
            fileType: null
        },
        componentValid: false
    }),
    validations() {
        let outputObject = {
            form: {
                sourceURL: {
                    // TODO validate URL properly
                    required,
                    url
                },
                fileType: {
                    required
                }
            }
        };
        return outputObject;
    },
    methods: {
        inputFileTypeChanged: function(event) {
            this.$v.form.fileType.$touch();
            if (
                this.$v.form.fileType.$dirty &&
                this.$v.form.fileType.$invalid
            ) {
                console.log("filetype invalid");
                return;
            }

            this.checkFormValid();
            return;
        },
        inputURLChanged: function(event) {
            this.$v.form.sourceURL.$touch();
            if (
                this.$v.form.sourceURL.$dirty &&
                this.$v.form.sourceURL.$invalid
            ) {
                console.log("sourceurl invalid");
                return;
            }

            this.checkFormValid();
            return;
        },
        checkFormValid: function() {
            if (
                !this.$v.form.sourceURL.$dirty ||
                !this.$v.form.fileType.$dirty
            ) {
                return;
            }
            this.$v.$touch();

            // emit validity value
            if (this.componentValid != this.$v.$dirty && !this.$v.$invalid) {
                this.componentValid = this.$v.$dirty && !this.$v.$invalid;
                this.$emit("update-component-validity", this.componentValid);
                console.log(
                    "update-component-validity, " + this.componentValid
                );
            }

            if (!this.componentValid) {
                return;
            }

            this.$emit(
                "input-changed",
                this.form.sourceURL,
                this.form.fileType
            );
        }
    },
    computed: {
        fileTypes: function() {
            let fileTypesLC = Object.keys(this.fileTypeMapping).map(type =>
                type.toLowerCase()
            );
            let fileTypes = [...new Set(fileTypesLC)];
            return fileTypes;
        },
        validationSourceURL: function() {
                return this.$v.form.sourceURL.$dirty ? !this.$v.form.sourceURL.$invalid : null;
        },
        validationFileType: function() {
            return this.$v.form.fileType.$dirty ? !this.$v.form.fileType.$invalid : null;
        },
        urlErrorMsg: function() {
            let url = this.form.sourceURL.toLowerCase();
            if (!url.startsWith("https://") && !url.startsWith("http://")) {
                return "Add protocol in front (e.g. https://)";
            }
            return "";
        }
    }
};
</script>
