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
                            :class="getMetadataLayoutClass(element.id)"
                            v-for="field in getFields(element.id)"
                            :key="`${field}-${element.id}`"
                        >
                            <md-field
                                :class="{
                                    'md-invalid':
                                        $v.elements[element.id][field]
                                            .$invalid &&
                                        $v.elements[element.id][field].$dirty,
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
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "step4BulkDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        fileInformation: Object,
        fileTypeMapping: Object,
    },
    data: () => ({
        datasetSaved: false,
        sending: false,
        elements: [],
        datasetMetadataMapping: undefined,
    }),
    computed: {},
    validations: function () {
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
        getMetadataLayoutClass: function (id) {
            let fields = this.getFields(id);
            let sizeQualifier = Math.round(60 / fields.length / 5) * 5;
            return `md-layout-item md-size-${sizeQualifier}`;
        },
        getFields: function (id) {
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
        getFieldOptions: function (id, field) {
            const valueType = this.fileInformation[id].ValueType;
            const fileType = this.getFileType(
                this.fileInformation[id].filename
            );
            return this.datasetMetadataMapping[fileType]["ValueType"][
                valueType
            ][field];
        },
        getFileType: function (filename) {
            let fileEnding = filename.split(".").pop();
            return this.fileTypeMapping[fileEnding];
        },
        clearForm() {
            this.$v.$reset();
            this.initializeFields();
        },
        saveDataset: async function () {
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
        initializeFields() {
            this.elements = [];
            for (let id of Object.keys(this.fileInformation)) {
                let tempObject = {
                    id: id,
                    datasetName: this.fileInformation[id].datasetName,
                    assembly: this.fileInformation[id].assembly,
                    perturbation: this.fileInformation[id].perturbation,
                    cellCycleStage: this.fileInformation[id].cellCycleStage,
                    ValueType: this.fileInformation[id].ValueType,
                    file: this.fileInformation[id].file,
                    public: this.fileInformation[id].public,
                    state: undefined,
                };
                for (let field of this.getFields(id)) {
                    tempObject[field] = null;
                }
                this.elements.push(tempObject);
            }
        },
    },
    mounted: function () {
        this.datasetMetadataMapping =
            this.$store.getters["getDatasetMetadataMapping"]["DatasetType"];
        this.initializeFields();
    },
    watch: {},
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
