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
                  :disabled="!coolersAvailable"
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
                  :disabled="!bedFilesAvailable"
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
              <md-field :class="getValidationClass('windowsizes')">
                <label for="windowsizes">Windowsizes</label>
                <md-select
                  id="windowsizes"
                  name="windowsizes"
                  v-model="form.windowsizes"
                  md-dense
                  :disabled="!pileupRegionsAvailable"
                  required
                  multiple>
                    <md-option
                    v-for="item in availablePileupRegions"
                    :value="item.windowsize"
                    :key="item.windowsize"
                    >{{ item.windowsize }}</md-option>
                </md-select>
                <span class="md-error" v-if="!$v.form.windowsizes.required"
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
        <md-button
            class="md-dense md-raised md-primary md-icon-button md-alignment-horizontal-left"
            @click="fetchDatasets"
            >
          <md-icon>cached</md-icon>
        </md-button>
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
import { group_pileupregions_on_windowsize } from "../functions"

export default {
  name: "proprocessDatasetForm",
  mixins: [validationMixin, apiMixin],
  data: () => ({
      availableCoolers: [],
      availableBinsizes: [10000, 20000, 50000],
      availableBedFiles: [],
      availablePileupRegions: [],
    form: {
      coolerID: null,
      binsizes: null,
      bedfileIDs: null,
      windowsizes: null,
    },
    datasetSaved: false,
    sending: false,
  }),
  computed: {
      coolersAvailable: function () {
          return this.availableCoolers.length != 0;
      },
      bedFilesAvailable: function () {
          return this.availableBedFiles.length != 0;
      },
      pileupRegionsAvailable: function () {
          return Object.keys(this.availablePileupRegions).length != 0;
      }
  },
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
      windowsizes: {
        required
      },
    },
  },
  methods: {
    fetchDatasets: function () {
      this.fetchData("datasets/").then((response) => {
        // success, store datasets
        this.$store.commit("setDatasets", response.data);
        // update datasets; Only use completed datasets; completed is 1 if completed, 0 if in progress and -1 if failed
        this.availableCoolers = response.data.filter(
          (element) => element.filetype == "cooler"
        );
        this.availableBedFiles = response.data.filter(
          (element) => element.filetype == "bedfile"
        );
      });
    },
    fetchPileupregions: async function (){
        var pileupRegions = [];
        var tempPileupRegions = {}
        for (var regionID of this.form.bedfileIDs){
            tempPileupRegions = await this.fetchPileupregion(regionID);
            pileupRegions.push(...tempPileupRegions.data)
        }
        this.availablePileupRegions = group_pileupregions_on_windowsize(pileupRegions);
    },
    fetchPileupregion: function (regionID) {
      return this.fetchData(`datasets/${regionID}/pileupregions/`)
    },
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
      this.form.windowsizes = null;
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
  watch: {
      'form.bedfileIDs': function() {
              this.fetchPileupregions()
          }
      },
  created: function () {
    this.fetchDatasets();
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
</style>