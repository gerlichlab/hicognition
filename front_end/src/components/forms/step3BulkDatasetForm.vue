<template>
    <b-container>
          <b-row
              v-for="element in elements"
              :key="element.id"
          >
            <b-col cols="3">
              <b-form-group label="Dataset Name">
                <b-form-input v-model="element.datasetName"></b-form-input>
              </b-form-group>
            </b-col>
            <b-col cols="2">
              <b-form-group label="Celltype">
                <b-form-input v-model="element.cellType"></b-form-input>
              </b-form-group>
            </b-col>
            <b-col cols="2">
              <b-form-group label="Perturbation">
                <b-form-input v-model="element.perturbation"></b-form-input>
              </b-form-group>
            </b-col>
            <b-col cols="5">
              <b-form-group label="Description">
                <b-form-input v-model="element.description"></b-form-input>
              </b-form-group>
            </b-col>
          </b-row>
    </b-container>
</template>

<script>
export default {
  props: {
    fileInformation: Array
  },
  data() {
    return {
      elements: []
    };
  },
  methods: {
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
      this.elements = this.file
      for (let id of Object.keys(this.fileInformation)) {
        let tempObject = {
          id: id,
          datasetName: this.fileInformation[id].datasetName,
          assembly: this.fileInformation[id].assembly,
          sizeType: this.fileInformation[id].sizeType,
          file: this.fileInformation[id].file,
          filename: this.fileInformation[id].name,
          public: this.fileInformation[id].public,
          perturbation: null,
          cellType: null,
          state: undefined,
          description: undefined
        };
        this.elements.push(tempObject);
      }
    },
  },
  mounted() {
    this.initializeFields();
  },
  watch: {
    fileInformation(val) {
      if (val) {
        this.elements = this.fileInformation;
      }
    },
  },
};
</script>
