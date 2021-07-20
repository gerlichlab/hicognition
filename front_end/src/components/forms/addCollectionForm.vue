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
                                :class="getValidationClass('name')"
                            >
                                <label :for="`name_collections-${fileType}`">Name</label>
                                <md-input
                                    :name="`name_collections-${fileType}`"
                                    :id="`name_collections-${fileType}`"
                                    v-model="form.name"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.name.required"
                                    >A collection name is required</span
                                >
                            </md-field>
                        </div>
                        <!-- Genotype field -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('used_datasets')">
                                <label :for="`used_datasets_collections-${fileType}`">Datasets</label>
                                <md-select
                                    :name="`used_datasets_collections-${fileType}`"
                                    :id="`used_datasets_collections-${fileType}`"
                                    v-model="form.used_datasets"
                                    multiple
                                    :disabled="sending"
                                >
                                    <md-option
                                        v-for="item in availableDatasets"
                                        :value="item.id"
                                        :key="item.id"
                                        >{{ item.dataset_name }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.used_datasets.required"
                                    >At least one dataset needs to be selected!</span
                                >
                            </md-field>
                        </div>
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
                        >Submit Collection</md-button
                    >
                    <md-button class="md-primary" @click="$emit('close-dialog')"
                        >Close</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >The collection was added succesfully and is ready for preprocessing!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";



export default {
    name: "AddCollectionForm",
    mixins: [validationMixin, apiMixin],
    props: {
        fileType: String
    },
    data: () => ({
        form: {
            name: null,
            used_datasets: []
        },
        datasetSaved: false,
        sending: false,
        availableDatasets: []
    }),
    validations: {
        // validators for the form
        form: {
            name: {
                required
            },
            used_datasets: {
                required
            }
        }
    },
    computed: {
    },
    methods: {
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.form[fieldName];

            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty
                };
            }
        },
        fetchDatasets: function() {
            // fetches available datasets (cooler and bedfiles) from server
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                this.$store.commit("setDatasets", response.data);
                // update datasets
                this.availableDatasets = response.data.filter(
                    element =>
                    {
                        if (this.fileType == "bedfile"){
                            return element.filetype == "bedfile"
                        }else{
                            return element.filetype == "bigwig"
                        }
                    }
                );
            });
        },
        clearForm() {
            this.$v.$reset();
            this.form.name   = null;
            this.form.used_datasets = []
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            // var formData = new FormData();
            // for (var key in this.form) {
            //     if (key == "file") {
            //         // file data needs to be included like this because the form data only contains the filename at this stage
            //         formData.append(
            //             key,
            //             this.selectedFile,
            //             this.selectedFile.name
            //         );
            //     } else {
            //         formData.append(key, this.form[key]);
            //     }
            // }
            // // add filetype
            // formData.append("filetype", this.selectedFileType);
            // // API call including upload is made in the background
            // this.postData("datasets/", formData).then(response => {
            //     this.sending = false;
            //     this.clearForm();
            //     if (response) {
            //         // if error happend, global error handler will eat the response
            //         this.datasetSaved = true;
            //     }
            // });
            setTimeout(() => {
                this.sending = false
            }, 500)
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    mounted: function(){
        this.fetchDatasets()
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
