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
                        :key="element.id"
                    >
                        <div class="md-layout-item md-size-20">
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
                        <!-- Now, iteration over fields of element --->

                        <div
                            class="md-layout-item md-size-20"
                            v-for="field in getFields(element.id)"
                            :key="`${field}-${element.id}`"
                        >
                            <md-field
                                :class="{
                                    'md-invalid':
                                        $v.elements[element.id][field]
                                            .$invalid &&
                                        $v.elements[element.id][field].$dirty
                                }"
                            >
                                <label :for="`${field}-${element.id}`">{{
                                    field
                                }}</label>

                                <md-select
                                    :name="`${field}-${element.id}`"
                                    :id="`${field}-${element.id}`"
                                    v-model="element[field]"
                                    required
                                    :disabled="sending"
                                    v-if="
                                        getFieldOptions(element.id, field) !=
                                            'freetext'
                                    "
                                >
                                    <md-option
                                        v-for="option in getFieldOptions(
                                            element.id,
                                            field
                                        )"
                                        :key="option"
                                        :value="option"
                                        >{{ option }}</md-option
                                    >
                                </md-select>
                                <md-input
                                    :name="`${field}-${element.id}`"
                                    :id="`${field}-${element.idid}`"
                                    v-model="element[field]"
                                    :disabled="sending"
                                    required
                                    v-else
                                />
                                <span
                                    class="md-error"
                                    v-if="
                                        !$v.elements[element.id][field].required
                                    "
                                    >A ValueType is required</span
                                >
                            </md-field>
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
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "step4BulkDatasetForm",
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
    validations: function() {
        let outputObject = { elements: {} };
        for (let element of this.elements) {
            let fields = this.getFields(element.id);
            for (let field of fields) {
                if (!(element.id in outputObject["elements"])) {
                    outputObject["elements"][element.id] = {};
                }
                outputObject["elements"][element.id][field] = { required };
            }
        }
        return outputObject;
    },
    methods: {
        getFields: function(id) {
            let filename = this.fileInformation[id].filename;
            let valueType = this.fileInformation[id].ValueType;
            if (!valueType) {
                return [];
            }
            const fileType = this.getFileType(filename);
            return Object.keys(
                this.datasetMetadataMapping[fileType]["ValueType"][valueType]
            );
        },
        getFieldOptions: function(id, field) {
            const valueType = this.fileInformation[id].ValueType;
            const fileType = this.getFileType(
                this.fileInformation[id].filename
            );
            return this.datasetMetadataMapping[fileType]["ValueType"][
                valueType
            ][field];
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
        },
        initializeFields() {
            for (let id of Object.keys(this.fileInformation)) {
                let tempObject = {
                    id: id,
                    datasetName: this.fileInformation[id].datasetName,
                    state: undefined
                };
                for (let field of this.getFields(id)) {
                    tempObject[field] = null;
                }
                this.elements.push(tempObject);
            }
        }
    },
    mounted: function() {
        this.datasetMetadataMapping = this.$store.getters[
            "getDatasetMetadataMapping"
        ]["DatasetType"];
        this.initializeFields();
    },
    watch: {}
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
