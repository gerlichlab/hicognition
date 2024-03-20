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
                    <div
                        class="md-layout md-gutter"
                        v-for="element in elements"
                        :set="(v = $v.elements.$each[element.id])"
                        :key="element.id"
                    >
                        <div class="md-layout-item md-size-25">
                            <md-field style="overflow-x: auto">
                                {{ element.filename }}
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-15">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.assembly.$invalid && v.assembly.$dirty
                                }"
                            >
                                <label :for="`assembly-${element.id}`"
                                    >Assembly</label
                                >

                                <md-select
                                    :name="`assembly-${element.id}`"
                                    :id="`assembly-${element.id}`"
                                    v-model="element.assembly"
                                    required
                                    :disabled="sending"
                                >
                                    <md-optgroup
                                        v-for="(values, org) in assemblies"
                                        :key="org"
                                        :label="org"
                                    >
                                        <md-option
                                            v-for="assembly in values"
                                            :key="assembly.id"
                                            :value="assembly.id"
                                            >{{ assembly.name }}</md-option
                                        >
                                    </md-optgroup>
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!v.assembly.required"
                                    >A genome assembly is required</span
                                >
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-25">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.datasetName.$invalid &&
                                        v.datasetName.$dirty
                                }"
                            >
                                <label :for="`name-${element.id}`">Name</label>
                                <md-input
                                    :name="`name-${element.id}`"
                                    :id="`name-${element.id}`"
                                    v-model="element.datasetName"
                                    :disabled="sending"
                                    maxlength="30"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.datasetName.required"
                                    >A dataset name is required</span
                                >
                                <span
                                    class="md-error"
                                    v-if="!v.datasetName.maxLength"
                                    >Maximum length exceeded</span
                                >
                            </md-field>
                        </div>
                        
                        <div class="md-layout-item md-size-10">
                            <md-field
                                :class="{
                                        'md-invalid':
                                            v.sample_id.$invalid &&
                                            v.sample_id.$dirty
                                    }"
                            >
                                <label :for="`sample_id-${element.id}`"
                                    >Sample ID</label
                                >
                                <md-input
                                    :name="`sample_id-${element.id}`"
                                    :id="`sample_id-${element.id}`"
                                    v-model="element.sample_id"
                                    :disabled="sending"
                                    maxlength="128"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.sample_id.required"
                                    >A sample ID is required</span
                                >
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-15" v-if="isRegion">
                            <md-field 
                                :class="{
                                    'md-invalid':
                                        v.sizeType.$invalid &&
                                        v.sizeType.$dirty
                                }"
                            >
                                <label :for="`sizeType-${element.id}`">SizeType</label>
                                <md-select
                                    :name="`sizeType-${element.id}`"
                                    :id="`sizeType-${element.id}`"
                                    v-model="element.sizeType"
                                    :disabled="sending"
                                    required
                                >
                                    <md-option value="Point">Point</md-option>
                                    <md-option value="Interval">Interval</md-option>
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!v.sizeType.required"
                                    >A size type is required for regions</span
                                >
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-10">
                            <md-checkbox
                                v-model="element.public"
                                true-value="true"
                                false-value="false"
                                class="top-margin"
                                >Public</md-checkbox
                            >
                        </div>
                    </div>
                </md-card-content>
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
import { required, requiredIf, maxLength, minLength} from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "step2BulkDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        files: FileList,
        fileTypeMapping: Object
    },
    data: () => ({
        datasetSaved: false,
        sending: false,
        assemblies: {},
        elements: [],
        datasetMetadataMapping: undefined
    }),
    computed: {
        isRegion: function() {
            if (!this.files){
                return
            }
            for (let i = 0; i < this.files.length; i++) {
                if (this.getFileType(this.files[i].name) == 'bedfile'){
                    return true
                }
            }
            return false
        }
    },
    validations: {
        elements: {
            $each: {
                datasetName: {
                    required,
                    minLength: minLength(3),
                    maxLength: maxLength(30)
                },
                sizeType: {
                    required: requiredIf(function (value, vam){
                        return this.isRegion
                })
                },
                sample_id: {
                    required,
                    minLength: minLength(3),
                    maxLength: maxLength(128)
                },
                assembly: { required },
                public: {}
            }
        }
    },
    methods: {
        getFileType: function(filename) {
            let fileEnding = filename.split(".").pop();
            return this.fileTypeMapping[fileEnding];
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then(response => {
                if (response) {
                    this.assemblies = response.data;
                }
            });
        },
        getFileType: function(filename) {
            let fileEnding = filename.split(".").pop();
            return this.fileTypeMapping[fileEnding];
        },
        clearForm() {
            this.$v.$reset();
            this.elements = [];
            for (let i = 0; i < this.files.length; i++) {
                var tempObject = {
                    id: i,
                    datasetName: null,
                    sample_id: null,
                    assembly: null,
                    sizeType: null,
                    filename: this.files[i].name,
                    file: this.files[i],
                    public: true
                };
                this.elements.push(tempObject);
            }
        },
        saveDataset: async function() {
            this.sending = true; // show progress bar
            // emit data
            let information = {};
            for (let element of this.elements) {
                information[element.id] = element;
            }
            this.$emit("step-completion", information);
            this.clearForm();
            this.sending = false;
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    mounted: function() {
        this.assemblies = this.fetchAssemblies();
        this.datasetMetadataMapping = this.$store.getters[
            "getDatasetMetadataMapping"
        ]["DatasetType"];
    },
    watch: {
        files: function(val) {
            if (val) {
                for (let i = 0; i < this.files.length; i++) {
                    var tempObject = {
                        id: i,
                        datasetName: null,
                        sample_id: null,
                        assembly: null,
                        sizeType: null,
                        filename: this.files[i].name,
                        file: this.files[i],
                        public: false
                    };
                    this.elements.push(tempObject);
                }
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.md-card {
    max-height: none;
}

.md-progress-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
}
.top-margin {
    margin-top: 30px;
}

.component-fade-enter-active {
    transition: opacity 0s linear;
}

.component-fade-leave-active {
    transition: opacity 0.1s linear;
}
.component-fade-enter, .component-fade-leave-to
/* .component-fade-leave-active below version 2.1.8 */ {
    opacity: 0;
}
</style>
