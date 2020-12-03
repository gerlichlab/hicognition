<template>
  <div>
    <md-dialog :md-active.sync="showDialog">
      <md-dialog-title>Preprocess Dataset
      </md-dialog-title>
        <preprocessDatasetForm @close-dialog="$emit('close-dialog')"></preprocessDatasetForm>
    </md-dialog>

  </div>
</template>

<script>
import preprocessDatasetForm from "./preprocessDatasetForm"

export default {
    name: 'DialogCustom',
    components: {
       preprocessDatasetForm
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function () {
            return this.dialog
        }
    }
  }
</script>

<style lang="scss" scoped>
  .md-dialog /deep/.md-dialog-container {
    max-width: 1000px;
  }

.md-dialog-actions {
    display: inline;
}
</style>