<template>
<div>
    <md-toolbar class="md-transparent" md-elevation="0">Manage datasets</md-toolbar>
    <md-list>
      <md-list-item>
        <md-button class="md-icon-button" @click="$emit('add-dataset-click')">
          <md-icon>add</md-icon>
        </md-button>
        <span class="md-list-item-text">Add Dataset</span>
      </md-list-item>

      <md-list-item>
        <md-button class="md-icon-button" @click="$emit('add-metadata-click')">
          <md-icon>highlight_alt</md-icon>
        </md-button>
        <span class="md-list-item-text">Add Metadata</span>
      </md-list-item>

      <md-list-item>
        <md-button class="md-icon-button" @click="$emit('preprocess-dataset-click')">
          <md-icon>launch</md-icon>
        </md-button>
        <span class="md-list-item-text">Preprocess Hi-C</span>
      </md-list-item>

      <md-list-item>
        <md-button class="md-icon-button" @click="$emit('preprocess-bigwig-click')">
          <md-icon>launch</md-icon>
        </md-button>
        <span class="md-list-item-text">Preprocess BigWig</span>
      </md-list-item>


      <md-list-item>
        <md-button class="md-icon-button" @click="$emit('mydataset-click')">
          <md-icon>list</md-icon>
        </md-button>
        <span class="md-list-item-text">My Datasets</span>
      </md-list-item>
    </md-list>
</div>
</template>

<script>
export default {
  name: "drawer"
};
</script>