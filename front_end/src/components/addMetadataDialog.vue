<template>
  <div>
    <md-dialog :md-active.sync="showDialog">
      <md-dialog-title>Add Metadata
      </md-dialog-title>
        <addMetadataForm @close-dialog="$emit('close-dialog')"></addMetadataForm>
    </md-dialog>

  </div>
</template>

<script>
import addMetadataForm from "./addMetadataForm"

export default {
    name: 'DialogCustom',
    components: {
      addMetadataForm
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