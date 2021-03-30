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
          <div class="md-layout md-gutter">
            <!-- Possible metadata fields -->
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('metadataFields')">
                <label for="metadataFields">Metadata Fields</label>
                <md-select
                  name="metadataFields"
                  id="metadataFields"
                  v-model="form.metadataFields"
                  md-dense
                  :disabled="!fieldsAvailable"
                  required
                  multiple
                >
                  <md-option
                    v-for="item in availableFields"
                    :value="item"
                    :key="item"
                    >{{ item }}</md-option
                  >
                </md-select>
                <span class="md-error" v-if="!$v.form.metadataFields.required"
                  >Field selection is required</span
                >
              </md-field>
            </div>
          </div>
        </md-card-content>
        <!-- Progress bar -->
        <md-progress-bar md-mode="indeterminate" v-if="sending" />
        <!-- Buttons for submission and closing -->
        <md-card-actions>
          <md-button type="submit" class="md-primary" :disabled="sending"
            >Set Metadata Fields</md-button
          >
          <md-button class="md-primary" @click="$emit('close-dialog')"
            >Close</md-button
          >
        </md-card-actions>
      </md-card>
      <!-- Submission notification -->
      <md-snackbar :md-active.sync="datasetSaved"
        >Fields were selected successfully</md-snackbar
      >
    </form>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import {
  required,
} from "vuelidate/lib/validators";
import { apiMixin } from "../mixins";

export default {
  name: "addMetadataFields",
  mixins: [validationMixin, apiMixin],
  data: () => ({
    form: {
      metadataFields: null,
    },
    availableFields: ["test1", "test2", "test3"],
    datasetSaved: false,
    sending: false
  }),
  validations: {
    // validators for the form
    form: {
      metadataFields: {
        required,
      }
    },
  },
  computed: {
      fieldsAvailable: function () {
          return this.availableFields.length != 0;
      },
  },
  methods: {
    getValidationClass(fieldName) {
      // matrial validation class for form field;
      const field = this.$v.form[fieldName];

      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty,
        };
      }
    },
    clearForm() {
      this.$v.$reset();
      this.form.metadataFields = null
    },
    saveDataset() {
      this.sending = true; // show progress bar
      // construct form data
      var formData = new FormData();
      for (var key in this.form){
            formData.append(key, this.form[key]);
      }
      // API call including upload is made in the background
      //this.postData("datasets/", formData);
      // show progress bar for 1.5 s
      window.setTimeout(() => {
        this.datasetSaved = true;
        this.sending = false;
        this.clearForm();
      }, 1500);
    },
    validateDataset() {
      this.$v.$touch();
      if (!this.$v.$invalid) {
        this.saveDataset();
      }
    },
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