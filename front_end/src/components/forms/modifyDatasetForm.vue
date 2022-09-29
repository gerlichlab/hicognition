<template>
    <div>
        <!-- Form definition -->
        <form
            novalidate
            class="md-layout"
            @submit.prevent="validateDataset"
            enctype="multipart/form-data"
        >
            <md-card class="md-layout-item">
                <!-- Field definitions -->
                <md-card-content>
                    <!-- Dataset name ande genotyp; first row -->
                    <div class="md-layout md-gutter">
                        <!-- dataset name -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field
                                :class="getValidationClass('datasetName')"
                            >
                                <label for="dataset-name">Name</label>
                                <md-input
                                    name="dataset-name"
                                    id="dataset-name"
                                    v-model="form.datasetName"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.datasetName.required"
                                    >A dataset name is required</span
                                >
                                <span
                                    class="md-error"
                                    v-else-if="!$v.form.datasetName.minlength"
                                    >Invalid dataset name</span
                                >
                            </md-field>
                        </div>
                    </div>
                    <!-- Second row -->
                    <div class="md-layout md-gutter">
                        <!-- public checkbox -->
                        <div class="md-layout-item md-small-size-100">
                            <md-checkbox
                                v-model="form.public"
                                class="top-margin"
                                >Public</md-checkbox
                            >
                        </div>
                    </div>
                    <!-- metadata -->
                    <div v-if="showMetadata">
                        <md-divider />
                        <md-list>
                            <md-subheader>Dataset descriptions</md-subheader>
                            <md-list-item>
                                <div class="md-layout md-gutter">
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="
                                                getValidationClass(
                                                    'perturbation'
                                                )
                                            "
                                        >
                                            <label for="perturbation"
                                                >Perturbation</label
                                            >
                                            <md-input
                                                name="perturbation"
                                                id="perturbation"
                                                v-model="form.perturbation"
                                                :disabled="sending"
                                                required
                                            />
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.perturbation
                                                        .required
                                                "
                                                >Perturbation information is
                                                required</span
                                            >
                                        </md-field>
                                    </div>
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="
                                                getValidationClass(
                                                    'cellCycleStage'
                                                )
                                            "
                                        >
                                            <label for="perturbation"
                                                >Cell cycle Stage</label
                                            >
                                            <md-input
                                                name="cellcycleStage"
                                                id="cellcycleStage"
                                                v-model="form.cellCycleStage"
                                                :disabled="sending"
                                                required
                                            />
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.cellCycleStage
                                                        .required
                                                "
                                                >Cell cycle stage is
                                                required</span
                                            >
                                        </md-field>
                                    </div>
                                </div>
                            </md-list-item>
                            <md-list-item>
                                <div class="md-layout md-gutter">
                                    <div
                                        class="md-layout-item md-small-size-100"
                                    >
                                        <md-field
                                            :class="
                                                getValidationClass('valueType')
                                            "
                                        >
                                            <label for="valueType"
                                                >Value Type</label
                                            >
                                            <md-select
                                                name="valueType"
                                                id="valueType"
                                                v-model="form.ValueType"
                                                required
                                                :disabled="sending"
                                            >
                                                <md-option
                                                    v-for="valueType in valueTypes"
                                                    :key="valueType"
                                                    :value="valueType"
                                                    >{{ valueType }}</md-option
                                                >
                                            </md-select>
                                            <span
                                                class="md-error"
                                                v-if="
                                                    !$v.form.ValueType.required
                                                "
                                                >A ValueType is required</span
                                            >
                                        </md-field>
                                    </div>
                                </div>
                            </md-list-item>
                            <md-list-item>
                                <div
                                    class="md-layout md-gutter"
                                    v-if="valueTypeSelected"
                                >
                                    <div
                                        class="md-layout-item md-small-size-100"
                                        v-for="field in valueTypeFields"
                                        :key="field"
                                    >
                                        <md-field
                                            :class="getValidationClass(field)"
                                        >
                                            <label for="valueType">{{
                                                field
                                            }}</label>

                                            <md-select
                                                :name="field"
                                                :id="field"
                                                v-model="form[field]"
                                                required
                                                :disabled="sending"
                                                v-if="
                                                    fieldOptions[field] !=
                                                        'freetext'
                                                "
                                            >
                                                <md-option
                                                    v-for="option in fieldOptions[
                                                        field
                                                    ]"
                                                    :key="option"
                                                    :value="option"
                                                    >{{ option }}</md-option
                                                >
                                            </md-select>
                                            <md-input
                                                :name="field"
                                                :id="field"
                                                v-model="form[field]"
                                                :disabled="sending"
                                                required
                                                v-else
                                            />
                                            <span
                                                class="md-error"
                                                v-if="!$v.form[field].required"
                                                >{{ field }} is required</span
                                            >
                                        </md-field>
                                    </div>
                                </div>
                            </md-list-item>
                        </md-list>
                        <md-divider />
                    </div>
                </md-card-content>
                <!-- Progress bar -->
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <!-- Buttons for submission and closing -->
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit dataset</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >The dataset was modified succesfully!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required, minLength } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "AddDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        datasetID: Number
    },
    data: () => ({
        form: {
            datasetName: null,
            public: true,
            ValueType: null,
            Normalization: null,
            Method: null,
            SizeType: null,
            Directionality: null,
            DerivationType: null,
            Protein: null,
            cellCycleStage: null,
            perturbation: null
        },
        datasetMetadataMapping: null,
        dataset: undefined,
        datasetSaved: false,
        sending: false,
        selectedFile: null,
        assemblies: {}
    }),
    validations() {
        // validators for the form
        let outputObject = {
            form: {
                datasetName: {
                    required,
                    minLength: minLength(3)
                },
                public: {},
                ValueType: {
                    required
                },
                cellCycleStage: {
                    required
                },
                perturbation: {
                    required
                }
            }
        };
        if (this.valueTypeSelected) {
            for (let key of Object.keys(
                this.datasetMetadataMapping[this.selectedFileType]["ValueType"][
                    this.form.ValueType
                ]
            ).filter(el => el != "SizeType")) {
                outputObject["form"][key] = { required };
            }
        }
        return outputObject;
    },
    computed: {
        selectedFileType: function() {
            if (!this.dataset) {
                return undefined;
            }
            return this.dataset.filetype;
        },
        valueTypeFields: function() {
            if (this.valueTypeSelected && this.selectedFileType) {
                return Object.keys(
                    this.datasetMetadataMapping[this.selectedFileType][
                        "ValueType"
                    ][this.form.ValueType]
                ).filter(el => el !== "SizeType");
            }
            return [];
        },
        fieldOptions: function() {
            if (this.valueTypeSelected && this.selectedFileType) {
                return this.datasetMetadataMapping[this.selectedFileType][
                    "ValueType"
                ][this.form.ValueType];
            }
            return undefined;
        },
        valueTypeSelected: function() {
            if (this.form.ValueType && this.selectedFileType) {
                return true;
            }
            return false;
        },
        valueTypes: function() {
            if (this.selectedFileType) {
                let valueTypes = Object.keys(
                    this.datasetMetadataMapping[this.selectedFileType][
                        "ValueType"
                    ]
                );
                // if there is only one value type, select it
                if (valueTypes.length == 1) {
                    this.$set(this.form, "ValueType", valueTypes[0]);
                }
                return valueTypes;
            }
            return undefined;
        },
        showMetadata: function() {
            // whether to show metadata fields
            if (this.selectedFileType) {
                return true;
            }
            return false;
        }
    },
    methods: {
        getDatasetFromStore: function() {
            this.dataset = this.$store.getters["getDataset"](this.datasetID);
        },
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.form[fieldName];

            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty
                };
            }
        },
        fetchDatasets() {
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                if (response) {
                    this.$store.commit("setDatasets", response.data);
                }
            });
        },
        saveDataset: function() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                // only include fields if they are not null
                if (this.form[key] !== null) {
                    formData.append(key, this.form[key]);
                }
            }
            // API call including upload is made in the background
            this.putData(`datasets/${this.dataset.id}/`, formData).then(
                async response => {
                    this.sending = false;
                    if (response) {
                        // if error happend, global error handler will eat the response
                        this.datasetSaved = true;
                        await this.fetchDatasets();
                        this.$emit("close-dialog");
                    }
                }
            );
        },
        populateFormWithData: function() {
            const fieldMapping = {
                dataset_name: "datasetName",
                valueType: "ValueType",
                cellCycleStage: "cellCycleStage",
                perturbation: "perturbation",
                method: "Method",
                directionality: "Directionality",
                protein: "Protein",
                derivationType: "DerivationType",
                normalization: "Normalization",
                public: "public"
            };
            for (let [key, value] of Object.entries(fieldMapping)) {
                if (value in this.form && this.dataset[key] !== undefined) {
                    this.form[value] = this.dataset[key];
                }
            }
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
        this.getDatasetFromStore();
        // populate form with data
        this.populateFormWithData();
    }
};
</script>

<style lang="scss" scoped>
.md-progress-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
}
.top-margin {
    margin-top: 24px;
}
</style>
