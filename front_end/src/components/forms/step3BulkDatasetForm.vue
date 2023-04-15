<template>
    <b-form @submit.prevent="validateDataset">
          <b-row v-for="(element, index) in elements" :key="index" class="mb-3">
            <b-col cols="3">
              <b-form-group label="Dataset Name">
                <b-form-input v-model="element.datasetName" disabled></b-form-input>
              </b-form-group>
            </b-col>
            <b-col cols="3">
              <b-form-group label="Celltype">
                <b-form-input v-model="element.cellType" required></b-form-input>
              </b-form-group>
            </b-col>
            <b-col cols="3">
              <b-form-group label="Perturbation">
                <b-form-input v-model="element.perturbation" required></b-form-input>
              </b-form-group>
            </b-col>
          </b-row>
    </b-form>
</template>

<script>
export default {
  props: {
    fileInformation: Array,
    fileTypeMapping: Object,
  },
  data() {
    return {
      elements: [],
      datasetMetadataMapping: undefined,
    };
  },
  methods: {
    getFileType(filename) {
      let fileEnding = filename.split(".").pop();
      return this.fileTypeMapping[fileEnding];
    },
    clearForm() {
      this.elements = [];
      this.initializeFields();
    },
    saveDataset: async function () {
      // Add any additional processing before sending the data
      for (let element of this.elements) {
        // Construct form data
        var formData = new FormData();
        for (let key in element) {
          if (
            key !== "id" &&
            key !== "filename" &&
            key !== "file" &&
            key !== "state"
          ) {
            formData.append(key, element[key]);
          }
        }
        // Add files
        formData.append("file", element.file, element.file.name);
        // Add filetype
        formData.append("filetype", this.getFileType(element.file.name));
        // Send the data
        await this.postData("datasets/", formData).then((response) => {
          if (!response) {
            this.sending = false;
            return;
          }
        });
      }
      this.clearForm();
      setTimeout(() => (this.datasetSaved = true), 200);
    },
    validateDataset() {
      this.$v.$touch();
      if (!this.$v.$invalid) {
        this.saveDataset();
      }
    },
    initializeFields() {
      this.elements = [];
      for (let id of Object.keys(this.fileInformation)) {
        let tempObject = {
          id: id,
          datasetName: this.fileInformation[id].datasetName,
          assembly: this.fileInformation[id].assembly,
          file: this.fileInformation[id].file,
          public: this.fileInformation[id].public,
          sizeType: this.fileInformation[id].sizeType,
          perturbation: null,
          cellType: null,
          state: undefined,
        };
        this.elements.push(tempObject);
      }
    },
  },
  mounted() {
    this.datasetMetadataMapping = this.$store.getters["getDatasetMetadataMapping"]["DatasetType"];
    this.initializeFields();
  },
  watch: {
    fileInformation(val) {
      if (val) {
        this.initializeFields();
      }
    },
  },
};
</script>
