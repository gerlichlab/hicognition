<template>

  <div class="half-width">
    <md-steppers :md-active-step.sync="active" md-linear>
      <md-step id="first" md-label="Upload Metadata file" :md-error="firstStepError" :md-editable="false" :md-done.sync="first">
        <addMetadataForm @close-dialog="$emit('close-dialog')" @success="handleMetadataAdditionSuccessful" @form-error="setError()"></addMetadataForm>
        <md-button class="md-raised md-primary" @click="setDone('first', 'second')" :disabled="blockSecondStep">Continue</md-button>
      </md-step>

      <md-step id="second" md-label="Specify Metadata fields" :md-editable="false" :md-done.sync="second">
        <addMetadataFieldsForm @close-dialog="$emit('close-dialog')" :availableFields="fields" :metadataID="metadataID"></addMetadataFieldsForm>
        <md-button class="md-raised md-primary" @click="setDone('second'); $emit('close-dialog')">Done</md-button>
      </md-step>

    </md-steppers>
  </div>
</template>

<script>

import addMetadataForm from "./addMetadataForm"
import addMetadataFieldsForm from "./addMetadataFieldsForm"


export default {
    name: "Metadata-stepper",
    components: {addMetadataForm, addMetadataFieldsForm},
    data: () => ({
      active: 'first',
      first: false,
      second: false,
      firstStepError: null,
      blockSecondStep: true,
      fields: [],
      metadataID: null
    }),
    methods: {
      setDone (id, index) {
        this[id] = true

        this.secondStepError = null

        if (index) {
          this.active = index
        }
      },
      handleMetadataAdditionSuccessful(event) {
        this.fields = event["field_names"]
        this.metadataID = event["id"]
        this.blockSecondStep = false;
        this.first = true;
        this.clearError();
      },
      setError () {
        this.firstStepError = 'Rownumber is not compatible!'
      },
      clearError() {
        this.firstStepError = null
      }
    }

}
</script>

<style lang="scss" scoped>

.half-width {
    width: 25vw;
}


</style>