<template>
    <div class="md-layout-item md-layout md-gutter">
        <div class="md-layout-item md-small-size-100">
        <md-field :class="validationSourceURL">
            <label for="sourceURL">URL</label>
            <md-input
                name="sourceURL"
                id="sourceURL"
                v-model="form.sourceURL"
                required
                @change="checkURLValid"
            />
            <span
                class="md-error"
                v-if="!$v.form.sourceURL.url"
                >Please check if URL is valid</span
            >
            <span
                class="md-error"
                v-if="!$v.form.sourceURL.required"
                >URL is required</span
            >
        </md-field>
        </div>
        <div class="md-layout-item md-small-size-100">
        <md-field :class="validationFileType">
            <label for="fileType">File type</label>
            <md-select
                id="fileType"
                name="fileType"
                v-model="form.fileType"
                required
                @md-selected="checkFileTypeValid"
            >
                <md-option v-for="fileType in fileTypes"
                    :key="fileType"
                    :value="fileType">
                    {{fileType}}
                </md-option>
            </md-select>

            <span
                class="md-error"
                v-if="!$v.form.fileType.url"
                >Filetype is required</span
            >
        </md-field>
        </div>
    </div>
</template>
<script>
import { validationMixin } from "vuelidate";
import { required, url } from "vuelidate/lib/validators";

export default {
    name: "formURLInput",
    props: ['fileTypeMapping'],
    emits: ['input-changed'],
    mixins: [validationMixin],
    data: () => ({
        form: {
            sourceURL: null,
            fileType: null
        }
    }),
    validations() {
        let outputObject = {
            form: {
                sourceURL: {
                    required,
                   // url
                },
                fileType: {
                    required
                }
            }
        };
        return outputObject; 
    },
    methods: {
        checkFileTypeValid: function(event) {
            this.$v.form.fileType.$touch();
            if (this.$v.form.fileType.$dirty && this.$v.form.fileType.$invalid) {
                console.log('filetype invalid');
                return;
            }

            this.checkFormValid();
            return;
        },
        checkURLValid: function(event) {
            this.$v.form.sourceURL.$touch();
            if (this.$v.form.sourceURL.$dirty && this.$v.form.sourceURL.$invalid) {
                console.log('sourceurl invalid');
                return;
            }

            this.checkFormValid();
            return;
        },
        checkFormValid: function() {
            if (this.$v.form.$invalid) {
                this.$emit('input-changed', null);
                console.log('form invalid');
                return;
            }

            this.$emit('input-changed', this.form.sourceURL, this.form.fileType);
        }
    },
    computed: {
        fileTypes: function() {
            let fileTypesLC = Object.keys(this.fileTypeMapping).map((type) => type.toLowerCase())
            let fileTypes = [...new Set(fileTypesLC)]
            return fileTypes
        },
        validationSourceURL: function() {
            return {'md-invalid': (this.$v.form.sourceURL.$dirty && this.$v.form.sourceURL.$invalid)}
        },
        validationFileType: function() {
            return {'md-invalid': (this.$v.form.fileType.$dirty && this.$v.form.fileType.$invalid)}
        }
    }
}
</script>