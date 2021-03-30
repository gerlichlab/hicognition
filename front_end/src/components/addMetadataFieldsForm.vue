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
              <md-field :class="getValidationClass('fields')">
                <label for="metadataFields">Metadata Fields</label>
                <md-select
                  name="metadataFields"
                  id="metadataFields"
                  v-model="form.fields"
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
                <span class="md-error" v-if="!$v.form.fields.required"
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
  props: {
      availableFields: Array,
      metadataID: Number
  },
  data: () => ({
    form: {
      fields: null,
    },
    datasetSaved: false,
    sending: false
  }),
  validations: {
    // validators for the form
    form: {
      fields: {
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
      this.form.fields = null
    },
    saveDataset() {
      this.sending = true; // show progress bar
      // construct form data
      var formData = new FormData();
      formData.append("fields", JSON.stringify(this.form["fields"]));
      // API call
      this.postData(`bedFileMetadata/${this.metadataID}/setFields`, formData).then(response => {
            if (!response){
                // error was caught and detected
                this.sending = false;
                this.clearForm();
            }else{
                this.datasetSaved = true;
                this.sending = false;
                this.$emit("success");
            }
      });
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