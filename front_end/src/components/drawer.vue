<template>
<div>
    <md-toolbar class="md-transparent" md-elevation="0">Manage datasets</md-toolbar>
    <md-list>
      <md-list-item>
        <md-button class="md-icon-button">
          <md-icon>move_to_inbox</md-icon>
        </md-button>
        <span class="md-list-item-text">Add Dataset</span>
      </md-list-item>

      <md-list-item>
        <md-button class="md-icon-button" @click="handleMyDataset">
          <md-icon>delete</md-icon>
        </md-button>
        <span class="md-list-item-text">My Datasets</span>
      </md-list-item>
    </md-list>
</div>
</template>

<script>
export default {
  name: "drawer",
  methods: {
    handleMyDataset: function () {
      this.$emit("mydataset-click");
    }
  }
};
</script>