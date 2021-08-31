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
                        <div class="md-layout-item md-size-30">
                            <md-field>
                                {{ element.filename }}
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-15">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.datasetName.$invalid &&
                                        v.datasetName.$dirty,
                                }"
                            >
                                <label :for="`name-${element.id}`">Name</label>
                                <md-input
                                    :name="`name-${element.id}`"
                                    :id="`name-${element.id}`"
                                    v-model="element.datasetName"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.datasetName.required"
                                    >A dataset name is required</span
                                >
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-10">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.assembly.$invalid &&
                                        v.assembly.$dirty,
                                }"
                            >
                                <label :for="`assembly-${element.id}`"
                                    >Assembly</label
                                >

                                <md-select
                                    :name="`assembly-${element.id}`"
                                    :id="`assembly-${element.id}`"
                                    v-model="element.assembly"
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

                        <div class="md-layout-item md-size-15">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.perturbation.$invalid &&
                                        v.perturbation.$dirty,
                                }"
                            >
                                <label :for="`perturbation-${element.id}`"
                                    >Perturbation</label
                                >
                                <md-input
                                    :name="`perturbation-${element.id}`"
                                    :id="`perturbation-${element.id}`"
                                    v-model="element.perturbation"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.perturbation.required"
                                    >Perturbation information is required</span
                                >
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-15">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.cellCycleStage.$invalid &&
                                        v.cellCycleStage.$dirty,
                                }"
                            >
                                <label :for="`cellCycleStage-${element.id}`"
                                    >Cell Cycle Stage</label
                                >
                                <md-input
                                    :name="`cellCycleStage-${element.id}`"
                                    :id="`cellCycleStage-${element.id}`"
                                    v-model="element.cellCycleStage"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.cellCycleStage.required"
                                    >Perturbation information is required</span
                                >
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-10">
                            <md-checkbox
                                v-model="element.public"
                                class="top-margin"
                                >Public</md-checkbox
                            >
                        </div>
                        <div class="md-layout-item md-size-5">
                            <transition name="component-fade" mode="out-in">
                                <md-icon
                                    class="top-margin"
                                    v-if="element.state == `finished`"
                                    >done</md-icon
                                >
                                <md-progress-spinner
                                    :md-diameter="30"
                                    md-mode="indeterminate"
                                    class="top-margin"
                                    v-if="element.state == 'processing'"
                                ></md-progress-spinner>
                            </transition>
                        </div>
                    </div>
                </md-card-content>
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit dataset</md-button
                    >
                </md-card-actions>
            </md-card>
            <md-snackbar :md-active.sync="datasetSaved"
                >The Datasets were added successfully and are ready for
                preprocessing!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "describeBulkDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        files: FileList,
        fileTypeMapping: Object,
    },
    data: () => ({
        datasetSaved: false,
        sending: false,
        assemblies: {},
        elements: [],
        datasetMetadataMapping: undefined,
    }),
    computed: {},
    validations: {
        elements: {
            $each: {
                datasetName: { required },
                assembly: { required },
                perturbation: { required },
                ValueType: { required },
                cellCycleStage: {required}
            },
        },
    },
    methods: {
        fetchAssemblies() {
            this.fetchData("assemblies/").then((response) => {
                if (response) {
                    this.assemblies = response.data;
                }
            });
        },
        getFileType: function (filename) {
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
                    assembly: null,
                    perturbation: null,
                    cellCycleStage: null,
                    ValueType: null,
                    filename: this.files[i].name,
                    file: this.files[i],
                    public: true,
                    state: undefined,
                };
                this.elements.push(tempObject);
            }
        },
        saveDataset: async function () {
            this.sending = true; // show progress bar
            // switch all datasets to processing
            for (let element of this.elements) {
                element.state = "processing";
            }
            // construct form data
            for (let element of this.elements) {
                // construct form data
                var formData = new FormData();
                for (let key in element) {
                    if (key != "id" && key != "fileanme" && key != "file") {
                        formData.append(key, element[key]);
                    }
                }
                // add files
                formData.append("file", element.file, element.file.name);
                // add filetype
                formData.append(
                    "filetype",
                    this.getFileType(element.file.name)
                );
                // send
                await this.postData("datasets/", formData).then((response) => {
                    if (!response) {
                        this.sending = false;
                        return;
                    }
                });
                // signal finished
                element.state = "finished";
            }
            this.clearForm();
            this.sending = false;
            setTimeout(() => (this.datasetSaved = true), 200);
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        },
    },
    mounted: function () {
        this.assemblies = this.fetchAssemblies();
        this.datasetMetadataMapping =
            this.$store.getters["getDatasetMetadataMapping"]["DatasetType"];
    },
    watch: {
        files: function (val) {
            if (val) {
                for (let i = 0; i < this.files.length; i++) {
                    var tempObject = {
                        id: i,
                        datasetName: null,
                        assembly: null,
                        filename: this.files[i].name,
                        file: this.files[i],
                        ValueType: null,
                        public: true,
                        state: undefined,
                        perturbation: null,
                        cellCycleStage: null,
                    };
                    this.elements.push(tempObject);
                }
            }
        },
    },
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
