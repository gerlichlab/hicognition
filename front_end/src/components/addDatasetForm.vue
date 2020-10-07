<template>
  <div>
    <form novalidate class="md-layout" @submit.prevent="validateDataset" enctype="multipart/form-data">
      <md-card class="md-layout-item">
        <md-card-content>
          <div class="md-layout md-gutter">
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('datasetName')">
                <label for="dataset-name">Name</label>
                <md-input
                  name="dataset-name"
                  id="dataset-name"
                  v-model="form.datasetName"
                  :disabled="sending"
                  required
                />
                <span class="md-error" v-if="!$v.form.datasetName.required"
                  >A dataset name is required</span
                >
                <span
                  class="md-error"
                  v-else-if="!$v.form.datasetName.minlength"
                  >Invalid dataset name</span
                >
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('genotype')">
                <label for="genotype">Genotype</label>
                <md-input
                  name="genotype"
                  id="genotype"
                  v-model="form.genotype"
                  :disabled="sending"
                />
              </md-field>
            </div>
          </div>

          <div class="md-layout md-gutter">
            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('filetype')">
                <label for="filetype">Filetype</label>
                <md-select
                  name="filetype"
                  id="filetype"
                  v-model="form.filetype"
                  md-dense
                  :disabled="sending"
                  required
                >
                  <md-option></md-option>
                  <md-option value="cooler">Cooler</md-option>
                  <md-option value="bedfile">Bedfile</md-option>
                </md-select>
                <span class="md-error">The filetype is required</span>
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100">
              <md-field :class="getValidationClass('file')">
                <label for="file">File</label>
                <md-file
                  id="file"
                  name="file"
                  v-model="form.file"
                  :disabled="sending"
                  @change="handleFileChange"
                  required
                />
                <span class="md-error" v-if="!$v.form.file.required"
                  >A file is required</span
                >
              </md-field>
            </div>
          </div>

          <md-field :class="getValidationClass('description')">
            <label for="description">Short Description</label>
            <md-textarea
              v-model="form.description"
              md-counter="80"
              maxlength="80"
              :disabled="sending"
            />
          </md-field>
        </md-card-content>

        <md-progress-bar md-mode="indeterminate" v-if="sending" />

        <md-card-actions>
          <md-button type="submit" class="md-primary" :disabled="sending"
            >Submit dataset</md-button
          >
          <md-button class="md-primary" @click="$emit('close-dialog')"
            >Close</md-button
          >
        </md-card-actions>
      </md-card>

      <md-snackbar :md-active.sync="userSaved"
        >The Dataset was submitted successfully!</md-snackbar
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

export default {
  name: "FormValidation",
  mixins: [validationMixin],
  data: () => ({
    form: {
      datasetName: null,
      genotype: null,
      filetype: null,
      file: null,
      description: null,
    },
    userSaved: false,
    sending: false,
    lastUser: null,
    selectedFile: null
  }),
  validations: {
    form: {
      datasetName: {
        required,
        minLength: minLength(3),
      },
      genotype: {},
      file: {
        required,
      },
      filetype: {
        required,
      },
      description: {
        maxLength: maxLength(80),
      },
    },
  },
  methods: {
    getValidationClass(fieldName) {
      const field = this.$v.form[fieldName];

      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty,
        };
      }
    },
    handleFileChange(event) {
        this.selectedFile = event.target.files[0];
    },
    clearForm() {
      this.$v.$reset();
      this.form.datasetName = null;
      this.form.genotype = null;
      this.form.file = null;
      this.form.filetype = null;
      this.form.description = null;
    },
    saveDataset() {
      this.sending = true;
      // get token
      var token = this.$store.state.token;
      var encodedToken = btoa(token + ":");
      // construct form data
      var formData = new FormData();
      for (var key in this.form){
          if (key == "file"){
              formData.append(key, this.selectedFile, this.selectedFile.name);
          }else{
            formData.append(key, this.form[key]);
          }
      }
      // API call including upload is made in the background
      this.$http
        .post(process.env.API_URL + "datasets/", formData, {
          headers: {
            "Authorization": `Basic ${encodedToken}`,
            "Content-Type": "multipart/form-data"
          },
        })
        .then((response) => {
          if (response.status != 200) {
            console.log(`Error: ${response.data}`);
          }
        }).catch(err => {
            console.log(`Error: ${err}`)
        });

      window.setTimeout(() => {
        this.userSaved = true;
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