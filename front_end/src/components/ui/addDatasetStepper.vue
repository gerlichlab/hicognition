<template>
    <b-container>
      <b-form @submit.prevent="validateDataset">
          <b-row
                v-for="(step, index) in steps"
                  :key="index"
                  class="mb-3"
          
          >
            <b-col>
              <b-list-group>
                <b-list-group-item>
                      <b-button
                        v-b-toggle="'collapse-' + index"
                        variant="info"
                        class="margin"
                      >
                        {{ step.label }}: {{ step.description }}
                      </b-button>


                    <b-collapse :id="'collapse-' + index" accordion="my-accordion">
                        <component
                          :is="step.component"
                          :files="files"
                          :fileInformation="fileInformation"
                          :fileTypeMapping="fileTypeMapping"
                          @step-completion="updateData"
                        ></component>
                    </b-collapse>
                </b-list-group-item>
              </b-list-group>
            </b-col>
          </b-row>
      </b-form>
    </b-container>
</template>


<script>
import step1FileUpload from "../forms/step1FileUpload.vue";
import step2DatasetInfo from "../forms/step2DatasetInfo.vue";
import step3BulkDatasetForm from "../forms/step3BulkDatasetForm.vue";

export default {
  components: {
    step1FileUpload,
    step2DatasetInfo,
    step3BulkDatasetForm,
  },
    props: {
        fileTypeMapping: Object
    },
  data() {
    return {
      steps: [
        {
          label: "Step 1",
          description: "Select files to upload",
          component: "step1FileUpload",
        },
        {
          label: "Step 2",
          description: "Add basic information",
          component: "step2DatasetInfo",
        },
        {
          label: "Step 3",
          description: "Add metadata",
          component: "step3BulkDatasetForm",
        },
      ],
      files: [],
      fileInformation: [],
    };
  },
  methods: {
    updateData(stepData) {
        console.log(stepData)
      // Process step data
      if (stepData.files) {
        this.files = stepData.files;
      }
      if (stepData.fileInformation) {
        this.fileInformation = stepData.fileInformation;
      }
    },
    validateDataset() {
      // Perform validation and submit the dataset
    },
  },
};
</script>

<style scoped>
.margin {
  margin-bottom: 10px;
}
</style>