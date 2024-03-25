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
                            <md-field>
                                <label :for="`name-${element.id}`"
                                    >Dataset name</label
                                >
                                <md-input
                                    :name="`name-${element.id}`"
                                    :id="`name-${element.id}`"
                                    v-model="element.datasetName"
                                    :disabled="true"
                                />
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-15">
                            <md-field>
                                <label :for="`celltype-${element.id}`"
                                    >Celltype</label
                                >
                                <md-input
                                    :name="`celltype-${element.id}`"
                                    :id="`celltype-${element.id}`"
                                    v-model="element.cellType"
                                    :disabled="sending"
                                    maxlength="60"
                                />
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-15">
                            <md-field>
                                <label :for="`perturbation-${element.id}`"
                                    >Perturbation</label
                                >
                                <md-input
                                    :name="`perturbation-${element.id}`"
                                    :id="`perturbation-${element.id}`"
                                    v-model="element.perturbation"
                                    :disabled="sending"
                                    maxlength="60"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-25">
                            <md-field>
                                <label :for="`description-${element.id}`"
                                    >Description</label
                                >
                                <md-input
                                    :name="`description-${element.id}`"
                                    :id="`description-${element.id}`"
                                    v-model="element.description"
                                    :disabled="sending"
                                    maxlength="80"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-10">
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
                        >Submit</md-button
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
import { apiMixin } from "../../mixins";
import { maxLength, required } from "vuelidate/lib/validators";

export default {
    name: "step3BulkDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        fileInformation: Object,
        fileTypeMapping: Object
    },
    data: () => ({
        datasetSaved: false,
        sending: false,
        elements: [],
        datasetMetadataMapping: undefined
    }),
    computed: {},
    validations: {
        elements: {
            $each: {
                perturbation: {
                    maxLength: maxLength(63)
                },
                cellType: {
                    maxLength: maxLength(63)
                },
                description: {
                    maxLength: maxLength(80)
                }
            }
        }
    },
    methods: {
        getFileType: function(filename) {
            let fileEnding = filename.split(".").pop();
            return this.fileTypeMapping[fileEnding];
        },
        clearForm() {
            this.$v.$reset();
            this.initializeFields();
        },
        saveDataset: async function() {
            this.sending = true; // show progress bar
            // switch all datasets to processing
            for (let element of this.elements) {
                element.state = "processing";
            }
            // form
            for (let element of this.elements) {
                // construct form data
                var formData = new FormData();
                for (let key in element) {
                    if (
                        key !== "id" &&
                        key !== "filename" &&
                        key !== "file" &&
                        key !== "state"
                    ) {
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
                await this.postData("datasets/", formData).then(response => {
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
        initializeFields() {
            this.elements = [];
            for (let id of Object.keys(this.fileInformation)) {
                let tempObject = {
                    id: id,
                    datasetName: this.fileInformation[id].datasetName,
                    assembly: this.fileInformation[id].assembly,
                    file: this.fileInformation[id].file,
                    public: this.fileInformation[id].public,
                    sizeType: this.fileInformation[id].sizeType,
                    sample_id: this.fileInformation[id].sample_id,
                    perturbation: null,
                    cellType: null,
                    description: null,
                    state: undefined
                };
                this.elements.push(tempObject);
            }
        }
    },
    mounted: function() {
        this.datasetMetadataMapping = this.$store.getters[
            "getDatasetMetadataMapping"
        ]["DatasetType"];
    },
    watch: {
        fileInformation: function(val) {
            if (val) {
                this.initializeFields();
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
