<template>
    <div class="md-layout-item md-small-size-100">
        <md-field :class='validationClass'>  <!--:class="getValidationClass('file')">-->
            <label for="file">File</label>
            <md-file
                id="file"
                name="file"
                v-model="form.file"
                @md-change="handleFileChange"
                :accept="acceptedFileTypes"
                required
            />
            <span
                class="md-error"
                v-if="!$v.form.file.required"
                >A file is required</span
            >
            <span
                class="md-error"
                v-else-if="!$v.form.file.validateFiletype"
            >
                Wrong filetype! 
            </span>
        </md-field>
    </div>
</template>


<script>
import { validationMixin } from "vuelidate";
import { required, minLength, maxLength, requiredIf, url } from "vuelidate/lib/validators";

export default {
    name: "formFileInput",
    props: ['fileTypeMapping'],
    emits: ['input-changed'],
    mixins: [validationMixin],
    data: () => ({
        form: {
            file: null
        },
        selectedFile: null
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
            return (fileEnding in this.fileTypeMapping);
        },
        handleFileChange(event) {
            // get file IO-stream
            this.$v.$touch();
            if (this.$v.$dirty && this.$v.$invalid) {
                console.log('input-changed');
                this.$emit('input-changed', null);
                return;
            }

            this.selectedFile = event[0];
            var nameSplit = event[0]['name'].split(".");
            this.fileExt = nameSplit[nameSplit.length - 1];
            this.$emit('input-changed', this.selectedFile);
        },
    },
    computed: {
        acceptedFileTypes: function() { // TODO sprint9
            // build accept parameter for file chooser, e.g. ".bed,.mcool,.bw"
            return "." + Object.keys(this.fileTypeMapping).join(',.')
        },
        validationClass: function() {
            return {'md-invalid': (this.$v.$dirty && this.$v.$invalid)}
        }
    }
}
</script>