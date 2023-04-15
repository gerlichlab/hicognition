<template>
  <b-form-group label="Sample ID">
    <b-form-input
      id="sampleID"
      v-model="form.sampleID"
      @change="fetchSampleMetadata"
      :state="validationState"
      required
    />
    <b-form-invalid-feedback v-if="!$v.form.sampleID.minLength">
      Sample ID must be at least 4 characters.
    </b-form-invalid-feedback>
    <b-form-invalid-feedback v-if="!$v.form.sampleID.sampleFound">
      Sample not found.
    </b-form-invalid-feedback>
    <b-form-invalid-feedback v-if="!$v.form.sampleID.accessAllowed">
      Access denied.
    </b-form-invalid-feedback>
    <b-form-invalid-feedback v-if="!$v.form.sampleID.fileTypeValid">
      Invalid file type.
    </b-form-invalid-feedback>
  </b-form-group>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required, minLength } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "formRepositoryInput",
    props: ["repository", "fileTypeMapping"],
    emits: ["input-changed", "update-component-validity"],
    mixins: [validationMixin, apiMixin],
    data: () => ({
        form: {
            sampleID: null
        },
        metadata: null,
        componentValid: false
    }),
    validations() {
        return {
            form: {
                sampleID: {
                    minLength: minLength(4),
                    required,
                    sampleFound: this.validSampleFound,
                    accessAllowed: this.validAccessAllowed,
                    fileTypeValid: this.validFileType
                }
            },
            fileExt: ""
        };
    },
    methods: {
        validSampleFound(event) {
            if (
                this.metadata &&
                this.metadata["status"] == "error" &&
                this.metadata["http_status_code"] == 404
            ) {
                return false;
            } else {
                return true;
            }
        },
        validAccessAllowed(event) {
            if (
                this.metadata &&
                this.metadata["status"] == "error" &&
                this.metadata["http_status_code"] == 403
            ) {
                return false;
            } else {
                return true;
            }
        },
        validFileType(event) {
            if (
                this.metadata &&
                this.metadata["status"] == "ok" &&
                this.metadata["json"] &&
                this.metadata["json"]["file_format"] &&
                this.metadata["json"]["file_format"]["file_format"]
            ) {
                this.fileExt = this.metadata["json"]["file_format"][
                    "file_format"
                ];
                return this.fileExt in this.fileTypeMapping;
            } else {
                return true;
            }
        },
        fetchSampleMetadata(event) {
            // check validity of form
            this.$v.$touch();
            if (!this.$v.$dirty) {
                return;
            }

            if (
                !(
                    this.$v.form.sampleID.required &&
                    this.$v.form.sampleID.minLength
                )
            ) {
                if (this.componentValid != false) {
                    this.componentValid = false;
                    this.$emit(
                        "update-component-validity",
                        this.componentValid
                    );
                    console.log(
                        "update-component-validity, " + this.componentValid
                    );
                }
                return;
            }
            this.fetchData(`ENCODE/${this.repository}/${this.form.sampleID}/`)
                .then(response =>
                    this.fetchSampleMetadataResponse(response.data)
                )
                .catch(error => this.fetchSampleMetadataError(error));
        },
        fetchSampleMetadataResponse: function(metadata) {
            this.metadata = metadata;
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
            // send to parent
            this.$emit(
                "input-changed",
                this.form.sampleID,
                this.metadata["json"]["file_format"]["file_format"],
                this.metadata
            );
            console.log(
                "input-changed" +
                    ", " +
                    this.form.sampleID +
                    ", " +
                    this.metadata["json"]["file_format"]["file_format"] +
                    ", " +
                    "{metadata}"
            );
        },
        fetchSampleMetadataError: function(error) {
            this.componentValid = false;
            this.$emit("update-component-validity", this.componentValid);
            console.log("update-component-validity, " + this.componentValid);
        }
    },
    computed: {
        acceptedFileTypes: function() {
            return "" + Object.keys(this.fileTypeMapping).join(", ");
        },
          validationState() {
            return this.$v.form.sampleID.$dirty ? !this.$v.form.sampleID.$invalid : null;
        }
    }
};
</script>
