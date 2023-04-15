<template>
  <b-container>
    <b-row>
        <b-col>
            <b-form-group>
                <b-form-file
                    v-model="files"
                    multiple
                    placeholder="Choose one or more files or drop them here..."
                    drop-placeholder="Drop files here..."
                ></b-form-file>
            </b-form-group>
        </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  data() {
    return {
      files: null,
    };
  },
  methods: {
    emitFiles() {
      this.$emit("step-completion", {files: this.files});
    },
  },
  watch: {
        files: {
            handler: function () {
                this.emitFiles();
            },
            deep: true
        }
   },
};
</script>
