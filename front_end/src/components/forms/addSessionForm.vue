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
                    <!-- Intervals for which annotations are added; first row -->
                    <div class="md-layout md-gutter">
                        <!-- Regions -->
                        <div class="md-layout-item md-small-size-100">
                            <md-field :class="getValidationClass('sessionName')">
                                <label for="sessionName">Session Name</label>
                                    <md-input
                                        name="sessionName"
                                        id="sessionName"
                                        v-model="form.sessionName"
                                        :disabled="sending"
                                    />
                                    <span
                                        class="md-error"
                                        v-if="!$v.form.sessionName.required"
                                        >Name is required</span
                                    >
                            </md-field>
                        </div>
                    </div>
                </md-card-content>
                <!-- Progress bar -->
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <!-- Buttons for submission and closing -->
                <md-card-actions>
                    <md-button class="md-primary" @click="$emit('close-dialog')"
                        >Close</md-button
                    >
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Save session</md-button
                    >
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >Session was saved succesfully!</md-snackbar
            >
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";

export default {
    name: "addSessionForm",
    mixins: [validationMixin, apiMixin],
    data: () => ({
        form: {
            sessionName: null
        },
        datasetSaved: false,
        sending: false
    }),
    validations: {
        // validators for the form
        form: {
            sessionName: {
                required
            }
        }
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
        clearForm() {
            this.$v.$reset();
            this.form.sessionName = null;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            // add name
            formData.append("name", this.form["sessionName"])
            // get session data
            var session_object = Object.assign({}, this.$store.getters["compare/getWidgetCollections"])
            var used_datasets = this.$store.getters["compare/getUsedDatasets"]
            var used_dataset_array;
            if (used_datasets.size == 0){
                used_dataset_array = []
            }else{
                used_dataset_array = Array.from(used_datasets.keys())
            }
            console.log(used_datasets);
            formData.append("session_object", JSON.stringify(session_object))
            formData.append("session_type", "compare")
            formData.append("used_datasets", JSON.stringify(used_dataset_array))
            // API call including upload is made in the background
            this.postData("sessions/", formData).then(response => {
                if (response){
                    this.datasetSaved = true;
                    this.sending = false;
                    this.clearForm();
                }else{
                    // no response means apiMixin caught an error, do not show success
                    this.sending = false;
                    this.clearForm();
                }
            });
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
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
