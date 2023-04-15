<template>
  <b-container>
    <b-row>
        <b-col>
            <b-form-group>
                <b-form-file
                    v-model="files"
                    multiple
                    placeholder="Choose one or more files or drop them here..."
                    drop-placeholder="Drop files here..."
                    invalid-feedback="Please select at least one file"
                    :state="getValidationState()"
                ></b-form-file>
                <b-form-invalid-feedback v-if="!$v.files.required">
                    Files are required.
                </b-form-invalid-feedback>
                <b-form-invalid-feedback v-else-if="!$v.files.correctFileType">
                    Wrong filetype.
                </b-form-invalid-feedback>
            </b-form-group>
        </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";

const correctFileType = function(value) {
    /* 
        validator for correct fileype. Note that this is the vue component in this example
    */
    for (let file of value) {
        let fileName = file.name;
        let splitFileName = fileName.split(".");
        let fileEnding = splitFileName[splitFileName.length - 1];
        if (!(fileEnding in this.fileTypeMapping)) {
            return false;
        }
    }
    return true
};





export default {
  mixins: [validationMixin],
      props: {
        fileTypeMapping: Object
    },
  data() {
    return {
      files: null,
    };
  },
  methods: {
    emitFiles() {
      this.$emit("step-completion", {files: this.files});
    },
        getValidationState() {
            // assigns validation state to form fields
            const field = this.$v.files;
            if (field) {
                return (field.$invalid && field.$dirty) ? false: null
            }
            return null;
        },
  },
  validations: {
    files: {
      required,
      correctFiletype: correctFileType
    },
  },
  watch: {
        files: {
            handler: function () {
              this.$v.$touch();
                this.emitFiles();
            },
            deep: true
        }
   },
};
</script>
