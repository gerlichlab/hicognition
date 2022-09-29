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
                            <md-field :class="getValidationClass('name')">
                                <label for="name">Name</label>
                                <md-input
                                    name="name"
                                    id="name"
                                    v-model="form.name"
                                    :disabled="sending || organisms.length == 0"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.name.required"
                                    >An assembly name is required</span
                                >
                            </md-field>
                        </div>
                        <!-- Organism field -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('organism')">
                                <label for="organism">Organism</label>
                                <md-select
                                    name="organism"
                                    id="organism"
                                    v-model="form.organism"
                                    :disabled="sending || organisms.length == 0"
                                >
                                    <md-option
                                        v-for="item in organisms"
                                        :value="item.id"
                                        :key="item.id"
                                        >{{ item.name }}</md-option
                                    >
                                </md-select>
                                <span
                                    class="md-error"
                                    v-if="!$v.form.organism.required"
                                    >An organism needs to be selected!</span
                                >
                            </md-field>
                        </div>
                    </div>
                    <!-- Second row -->
                    <div class="md-layout md-gutter">
                        <!-- chromosome sizes -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('chromSizes')">
                                <label for="chromSizes">Chromosome Sizes</label>
                                <md-file
                                    id="chromSizes"
                                    name="chromSizes"
                                    v-model="form.chromSizes"
                                    :disabled="sending || organisms.length == 0"
                                    @change="handleChromSizesChange"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.chromSizes.required"
                                    >A chromosome sizes file is required</span
                                >
                            </md-field>
                        </div>
                        <!-- file field -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('chromArms')">
                                <label for="chromArms">Chromosome arms</label>
                                <md-file
                                    id="chromArms"
                                    name="chromArms"
                                    v-model="form.chromArms"
                                    :disabled="sending || organisms.length == 0"
                                    @change="handleChromArmsChange"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!$v.form.chromArms.required"
                                    >A chromosome arms file is required</span
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
                        :disabled="sending || organisms.length == 0"
                        >Submit Genome</md-button
                    >
                    <md-button class="md-primary" @click="$emit('close-dialog')"
                        >Close</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >The Genome was added succesfully!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "AddAssemblyForm",
    mixins: [validationMixin, apiMixin],
    data: () => ({
        form: {
            name: null,
            organism: null,
            chromSizes: null,
            chromArms: null
        },
        organisms: [],
        datasetSaved: false,
        sending: false,
        selectedFiles: {
            chromSizes: null,
            chromArms: null
        }
    }),
    validations: {
        // validators for the form
        form: {
            name: {
                required
            },
            organism: {
                required
            },
            chromArms: {
                required
            },
            chromSizes: {
                required
            }
        }
    },
    methods: {
        fetchOrganisms: function() {
            this.fetchData("organisms/").then(response => {
                this.organisms = response.data;
            });
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
        handleChromSizesChange(event) {
            // get file IO-stream
            this.selectedFiles["chromSizes"] = event.target.files[0];
        },
        handleChromArmsChange(event) {
            // get file IO-stream
            this.selectedFiles["chromArms"] = event.target.files[0];
        },
        clearForm() {
            this.$v.$reset();
            this.form.name = null;
            this.form.organism = null;
            this.form.chromSizes = null;
            this.form.chromArms = null;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                if (["chromSizes", "chromArms"].includes(key)) {
                    // file data needs to be included like this because the form data only contains the filename at this stage
                    formData.append(
                        key,
                        this.selectedFiles[key],
                        this.selectedFiles[key].name
                    );
                } else {
                    formData.append(key, this.form[key]);
                }
            }
            // API call including upload is made in the background
            this.postData("assemblies/", formData).then(response => {
                this.sending = false;
                this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                }
            });
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    mounted: function() {
        this.fetchOrganisms();
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
