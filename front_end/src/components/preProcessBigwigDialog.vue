<template>
  <div>
    <md-dialog :md-active.sync="showDialog">
      <md-dialog-title>Preprocess BigWig Dataset
      </md-dialog-title>
        <preprocessBigwigForm @close-dialog="$emit('close-dialog')"></preprocessBigwigForm>
    </md-dialog>

  </div>
</template>

<script>
import preprocessBigwigForm from "./preprocessBigwigForm"

export default {
    name: 'DialogCustom',
    components: {
       preprocessBigwigForm
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: {
          set: function(value){
            if (!value){
              this.$emit('close-dialog')
            }
          },
          get: function() {
            return this.dialog
          }
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