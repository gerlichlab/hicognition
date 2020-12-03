<template>
  <div>
    <!-- Form definition -->
    <form novalidate class="md-layout" @submit.prevent="validateDataset" enctype="multipart/form-data">
      <md-card class="md-layout-item">
        <!-- Field definitions -->
        <md-card-content>
          <!-- Cooler file and binsizes; first row -->
          <div class="md-layout md-gutter">
            <!-- cooler file -->
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('coolerID')">
                <label for="coolerID">Cooler</label>
                <md-select
                  name="coolerID"
                  id="coolerID"
                  v-model="form.coolerID"
                  availableCoolers
                  :disabled="sending"
                  required>
                    <md-option
                    v-for="item in availableCoolers"
                    :value="item.id"
                    :key="item.id"
                    >{{ item.dataset_name }}</md-option>
                </md-select>
                <span class="md-error" v-if="!$v.form.coolerID.required">A dataset name is required</span>
              </md-field>
            </div>
            <!-- Binsizes field -->
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('binsizes')">
                <label for="binsizes">Binsizes</label>
                <md-select
                  name="binsizes"
                  id="binsizes"
                  v-model="form.binsizes"
                  :disabled="sending"
                  required
                  multiple>
                    <md-option
                    v-for="item in availableBinsizes"
                    :value="item"
                    :key="item"
                    >{{ item }}</md-option>
                </md-select>
                <span class="md-error" v-if="!$v.form.binsizes.required"
                  >Binsize selection is required</span
                >
              </md-field>
            </div>
          </div>
          <!-- Second row -->
          <div class="md-layout md-gutter">
            <!-- bedfiles -->
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('bedfileIDs')">
                <label for="bedfileIDs">Regions</label>
                <md-select
                  name="bedfileIDs"
                  id="bedfileIDs"
                  v-model="form.bedfileIDs"
                  md-dense
                  :disabled="sending"
                  required
                  multiple>
                    <md-option
                    v-for="item in availableBedFiles"
                    :value="item.id"
                    :key="item.id"
                    >{{ item.dataset_name }}</md-option>
                </md-select>
                <span class="md-error" v-if="!$v.form.bedfileIDs.required">Regions are required</span>
              </md-field>
            </div>
            <!-- windwosize -->
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('pileupRegionIDs')">
                <label for="pileupRegionIDs">Windowsizes</label>
                <md-select
                  id="pileupRegionIDs"
                  name="pileupRegionIDs"
                  v-model="form.pileupRegionIDs"
                  md-dense
                  :disabled="sending"
                  required
                  multiple>
                    <md-option
                    v-for="item in availablePileupRegions"
                    :value="item.id"
                    :key="item.id"
                    >{{ item.windowsize }}</md-option>
                </md-select>
                <span class="md-error" v-if="!$v.form.pileupRegionIDs.required"
                  >A windowsize is required!</span
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
            >Submit dataset</md-button
          >
          <md-button class="md-primary" @click="$emit('close-dialog')"
            >Close</md-button
          >
        </md-card-actions>
      </md-card>
      <!-- Submission notification -->
      <md-snackbar :md-active.sync="datasetSaved"
        >Preprocessing was started successfully!</md-snackbar
      >
    </form>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import {
  required,
  email,
  minLength,
  maxLength,
} from "vuelidate/lib/validators";
import { apiMixin } from "../mixins";

export default {
  name: "proprocessDatasetForm",
  mixins: [validationMixin, apiMixin],
  data: () => ({
      availableCoolers: [
          {
            "dataset_name": "test1",
            "id": 0
          },
          {
            "dataset_name": "test2",
            "id": 1
          }
      ],
      availableBinsizes: [10000, 20000, 50000],
      availableBedFiles: [
          {
            "dataset_name": "bedtest1",
            "id": 0
          },
          {
            "dataset_name": "bedtest2",
            "id": 1
          }
      ],
      availablePileupRegions: [
          {
            "name": "pileuptest1",
            "id": 0,
            "windowsize": 200000
          },
          {
            "name": "pileuptest2",
            "id": 1,
            "windowsize": 400000
          }
      ],
    form: {
      coolerID: null,
      binsizes: null,
      bedfileIDs: null,
      pileupRegionIDs: null,
    },
    datasetSaved: false,
    sending: false,
  }),
  validations: {
    // validators for the form
    form: {
      coolerID: {
        required
      },
      binsizes: {
        required,
      },
      bedfileIDs: {
        required,
      },
      pileupRegionIDs: {
        required
      },
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
      this.form.coolerID = null;
      this.form.binsizes = null;
      this.form.bedfileIDs = null;
      this.form.filetype = null;
      this.form.pileupregionIDs = null;
    },
    saveDataset() {
      this.sending = true; // show progress bar
      // construct form data
      var formData = new FormData();
      for (var key in this.form){
            formData.append(key, this.form[key]);
      }
      // API call including upload is made in the background
      this.postData("preprocess/", formData);
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
</style>