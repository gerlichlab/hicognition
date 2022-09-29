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

                        <div class="md-layout-item md-size-25">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.ValueType.$invalid &&
                                        v.ValueType.$dirty
                                }"
                            >
                                <label :for="`valueType-${element.id}`"
                                    >Value Type</label
                                >
                                <md-select
                                    :name="`valueType-${element.id}`"
                                    :id="`valueType-${element.id}`"
                                    v-model="element.ValueType"
                                    required
                                    :disabled="sending"
                                >
                                    <md-option
                                        v-for="valueType in getValueTypes(
                                            element.id
                                        )"
                                        :key="valueType"
                                        :value="valueType"
                                        >{{ valueType }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!v.ValueType.required"
                                    >A ValueType is required</span
                                >
                            </md-field>
                        </div>

                        <div class="md-layout-item md-size-25">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.perturbation.$invalid &&
                                        v.perturbation.$dirty
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

                        <div class="md-layout-item md-size-25">
                            <md-field
                                :class="{
                                    'md-invalid':
                                        v.cellCycleStage.$invalid &&
                                        v.cellCycleStage.$dirty
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
                                    >Cell cycle information is required</span
                                >
                            </md-field>
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
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

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
                perturbation: { required },
                ValueType: { required },
                cellCycleStage: { required }
            }
        }
    },
    methods: {
        getValueTypes: function(id) {
            const filename = this.fileInformation[id].filename;
            return Object.keys(
                this.datasetMetadataMapping[this.getFileType(filename)][
                    "ValueType"
                ]
            );
        },
        getFileType: function(filename) {
            let fileEnding = filename.split(".").pop();
            return this.fileTypeMapping[fileEnding];
        },
        clearForm() {
            this.$v.$reset();
            const numElements = this.elements.length;
            this.elements = [];
            for (let i = 0; i < numElements; i++) {
                var tempObject = {
                    datasetName: this.fileInformation[i].datasetName,
                    id: i,
                    perturbation: null,
                    cellCycleStage: null,
                    ValueType: null
                };
                this.elements.push(tempObject);
            }
        },
        saveDataset: async function() {
            this.sending = true; // show progress bar
            // emit data
            let information = {};
            for (let element of this.elements) {
                information[element.id] = Object.assign(
                    this.fileInformation[element.id],
                    element
                );
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
        this.datasetMetadataMapping = this.$store.getters[
            "getDatasetMetadataMapping"
        ]["DatasetType"];
    },
    watch: {
        fileInformation: function(val) {
            if (val) {
                for (let id of Object.keys(this.fileInformation)) {
                    var tempObject = {
                        id: id,
                        datasetName: this.fileInformation[id].datasetName,
                        ValueType: null,
                        perturbation: null,
                        cellCycleStage: null
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
