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
                        :set="v = $v.elements.$each[element.id]"
                        :key="element.id"
                    >
                        <div class="md-layout-item md-size-20">
                            <md-field
                            >
                                <label :for="`Filename-${element.id}`">Name</label>
                                <md-input
                                    :name="`Filename-${element.id}`"
                                    :id="`Filename-${element.id}`"
                                    :placeholder="element.filename"
                                    :disabled="true"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-field
                            :class="{ 'md-invalid': v.name.$invalid && v.name.$dirty }"
                            >
                                <label :for="`name-${element.id}`">Name</label>
                                <md-input
                                    :name="`name-${element.id}`"
                                    :id="`name-${element.id}`"
                                    v-model="element.name"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.name.required"
                                    >A dataset name is required</span
                                >
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-field
                            >
                                <label :for="`genotype-${element.id}`">Genotype</label>
                                <md-input
                                    :name="`genotype-${element.id}`"
                                    :id="`genotype-${element.id}`"
                                    v-model="element.genotype"
                                    :disabled="sending"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-field
                            >
                                <label :for="`description-${element.id}`">Description</label>
                                <md-input
                                    :name="`description-${element.id}`"
                                    :id="`description-${element.id}`"
                                    v-model="element.descriptions"
                                    :disabled="sending"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-checkbox
                                v-model="element.public"
                                class="top-margin"
                                >Public</md-checkbox
                            >
                        </div>
                    </div>
                </md-card-content>
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit dataset</md-button
                    >
                </md-card-actions>
            </md-card>
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";

export default {
    name: "describeBulkDatasetForm",
    mixins: [validationMixin],
    props: {
        files: FileList
    },
    data: () => ({
        datasetSaved: false,
        sending: false,
        elements: []
    }),
    computed: {
    },
    validations: {
        elements: {
            $each: {
                name: {required}
            }
        }
    },
    methods: {
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.elements[fieldName];

            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty
                };
            }
        },
        clearForm() {
            this.$v.$reset();
            console.log("clear form called")
            for (let i = 0; i < this.files.length; i++) {
                form[`name-${i}`] = null;
                form[`genotype-${i}`] = null;
                form[`description-${i}`] = null;
                form[`public-${i}`] = true;
            }
            return form;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // post forms
            console.log("sent")
            setTimeout(() => {
                this.sending = false;
            }, 500);
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    watch: {
        files: function(val){
            if (val){
                for (let i = 0; i < this.files.length; i++){
                var tempObject = {
                    id: i,
                    name: null,
                    genotype: null,
                    description: null,
                    filename: this.files[i].name,
                    public: true
                }
                this.elements.push(tempObject)
            }
            }
        }
    },
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
    margin-top: 30px;
}


</style>
