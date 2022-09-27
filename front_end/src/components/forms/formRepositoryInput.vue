<template>
    <div class="md-layout-item md-layout md-gutter">
        <div class="md-layout-item md-small-size-100">
        <md-field :class="validationSampleID">
            <label for="sampleID">Sample-ID</label>
            <md-input
                name="sampleID"
                id="sampleID"
                v-model="form.sampleID"
                required
                @change="fetchSampleMetadata"
            />
            <span
                class="md-error"
                v-if="!$v.form.sampleID.required"
                >Sample ID is required</span
            >
            <span
                class="md-error"
                v-else-if="!$v.form.sampleID.minLength"
                >Sample ID is too short</span
            >
            <span
                class="md-error"
                v-else-if="!$v.form.sampleID.validSampleFound"
                >No entry found for this sample ID</span 
            > <!-- TODO this triggers when file type is not right?! -->
            <span
                class="md-error"
                v-else-if="!$v.form.sampleID.validAccessAllowed"
                >Repository declined request (auth required)</span
            >
            <span
                class="md-error"
                v-else-if="!$v.form.sampleID.validFileType"
                >File type of entry is not allowed</span
            >
        </md-field>
        </div>
    </div>
</template>
<script>
import { validationMixin } from "vuelidate";
import { required, minLength } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "formRepositoryInput",
    props: ['repository', 'fileTypeMapping'],
    emits: ['input-changed'],
    mixins: [validationMixin, apiMixin],
    data: () => ({
        form: {
            sampleID: null
        },
        metadata: null
    }),
    validations() {
        return {
            form: {
                sampleID: {
                    minLength: minLength(4),
                    required,
                    sampleFound: this.validSampleFound,
                    validAccessAllowed: this.validAccessAllowed,
                    validFileType: this.validFileType
                }
            }
        };
    },
    methods: {
        validSampleFound(event) {
            if (this.metadata && this.metadata['status'] == 'error' && this.metadata['http_status_code'] == 404) {
                return false;
            } else {
                return true;
            }
        },
        validAccessAllowed(event) {
            if (this.metadata && this.metadata['status'] == 'error' && this.metadata['http_status_code'] == 403) {
                return false;
            } else {
                return true;
            }
        },
        validFileType(event) {
            if (this.metadata && this.metadata['status'] == 'ok' 
                && this.metadata['json'] 
                && this.metadata['json']['file_format']
                && this.metadata['json']['file_format']['file_format']) {
                var fileExt = this.metadata['json']['file_format']['file_format'];
                return (fileExt in this.fileTypeMapping);
            } else {
                return true;
            }
        },
        fetchSampleMetadata(event) {
            // 4DNFIRCHWS8M
            this.$v.form.sampleID.$touch();
            if (!(this.$v.form.sampleID.required && this.$v.form.sampleID.minLength)) {
                this.$emit('input-changed', null);
                return;
            }

            this.fetchData(`ENCODE/${this.repository}/${this.form.sampleID}/`)
                .then((response) => this.fetchSampleMetadataResponse(response.data))
                .catch((error) => this.fetchSampleMetadataError(error))
        },
        fetchSampleMetadataResponse: function (metadata) {
            this.metadata = metadata;
            this.$v.form.sampleID.$touch();
            if (this.$v.form.sampleID.$invalid) {
                this.$emit('input-changed', null);
                return;
            }
            // send to parent
            this.$emit('input-changed',
                this.form.sampleID,
                this.metadata['json']['file_format']['file_format'],
                this.metadata);
        },
        fetchSampleMetadataError: function (error) {
            this.metadata = undefined;
        },
    },
    computed: {
        validationSampleID: function() {
            return {'md-invalid': (this.$v.form.sampleID.$dirty && this.$v.form.sampleID.$invalid)}
        }
    }
}
</script>