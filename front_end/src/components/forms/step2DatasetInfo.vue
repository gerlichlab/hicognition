<template>
    <b-container>
        <b-row
            v-for="element in elements"
            :key="element.id"
            :set="(v = $v.elements.$each[element.id])"
        >
            <b-col cols="4">
                <b-form-group label="File name">
                    <b-form-input
                        v-model="element.filename"
                        disabled
                    ></b-form-input>
                </b-form-group>
            </b-col>
            <b-col cols="3">
                <b-form-group label="Dataset Name">
                    <b-form-input
                        v-model="element.datasetName"
                        required
                        :state="getValidationState(v.datasetName)"
                    ></b-form-input>
                    <b-form-invalid-feedback v-if="!v.datasetName.required">
                        A dataset name is required.
                    </b-form-invalid-feedback>
                    <b-form-invalid-feedback
                        v-else-if="!v.datasetName.minlength"
                    >
                        Invalid dataset name.
                    </b-form-invalid-feedback>
                </b-form-group>
            </b-col>
            <b-col cols="2">
                <b-form-group label="Assembly">
                    <b-form-select
                        id="assembly"
                        v-model="element.assembly"
                        :state="getValidationState(v.assembly)"
                    >
                        <b-form-select-option-group
                            v-for="(values, org) in assemblies"
                            :key="org"
                            :label="org"
                        >
                            <b-form-select-option
                                v-for="assembly in values"
                                :key="assembly.id"
                                :value="assembly.id"
                            >
                                {{ assembly.name }}
                            </b-form-select-option>
                        </b-form-select-option-group>
                    </b-form-select>
                    <b-form-invalid-feedback>
                        An assebmly is required.
                    </b-form-invalid-feedback>
                </b-form-group>
            </b-col>
            <b-col v-if="isRegion" cols="2">
                <b-form-group label="SizeType">
                    <b-form-select
                        v-model="element.sizeType"
                        :options="sizeTypes"
                        required
                        :state="getValidationState(v.sizeType)"
                    ></b-form-select>
                </b-form-group>
                <b-form-invalid-feedback>
                    A size type is required.
                </b-form-invalid-feedback>
            </b-col>
            <b-col cols="1" align-self="center">
                <b-form-group>
                    <b-form-checkbox v-model="element.public"
                        >Public</b-form-checkbox
                    >
                </b-form-group>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
import { validationMixin } from "vuelidate";
import { apiMixin } from "../../mixins";
import { required, requiredIf, maxLength } from "vuelidate/lib/validators";

export default {
    mixins: [validationMixin, apiMixin],
    props: {
        fileInformation: Array,
        files: Array,
        fileTypeMapping: Object
    },
    data() {
        return {
            elements: [],
            assemblies: [],
            sizeTypes: ["Point", "Interval"]
        };
    },
    validations: {
        elements: {
            $each: {
                datasetName: {
                    required,
                    maxLength: maxLength(30)
                },
                sizeType: {
                    required: requiredIf(function(value, vam) {
                        return this.isRegion;
                    })
                },
                assembly: { required },
                public: {}
            }
        }
    },
    methods: {
        emitDatasetInfo() {
            this.$emit("step-completion", {
                datasetName: this.datasetName,
                assembly: this.assembly,
                public: this.public
            });
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then(response => {
                if (response) {
                    this.assemblies = response.data;
                }
            });
        },
        getValidationState(field) {
            if (field) {
                return field.$invalid && field.$dirty ? false : null;
            }
        },
        getFileType: function(filename) {
            let fileEnding = filename.split(".").pop();
            return this.fileTypeMapping[fileEnding];
        }
    },
    computed: {
        isRegion: function() {
            if (!this.files) {
                return;
            }
            for (let i = 0; i < this.files.length; i++) {
                if (this.getFileType(this.files[i].name) == "bedfile") {
                    return true;
                }
            }
            return false;
        }
    },
    mounted: function() {
        this.assemblies = this.fetchAssemblies();
    },
    watch: {
        files: function(val) {
            if (val) {
                this.elements = [];
                for (let i = 0; i < this.files.length; i++) {
                    var tempObject = {
                        id: i,
                        datasetName: null,
                        assembly: null,
                        sizeType: null,
                        filename: this.files[i].name,
                        file: this.files[i],
                        public: false,
                        perturbation: null,
                        cellType: null,
                        state: undefined,
                        description: undefined
                    };
                    this.elements.push(tempObject);
                }
            }
        },
        elements: function(val) {
            this.$v.$touch();
            this.$emit("step-completion", { fileInformation: val });
        }
    }
};
</script>
