<template>
  <div>
    <!-- span window horizontal is needed to position logout on the right -->
    <div class="md-toolbar-row span-window-horizontal">
      <div class="md-toolbar-section-start">
        <md-button class="md-icon-button" @click="$emit('drawer-clicked')">
          <md-icon>menu</md-icon>
        </md-button>

        <span class="md-title">HiCognition 0.1</span>
      </div>

      <div class="md-toolbar-section-end">
        <md-button class="md-icon-button">
          <md-icon>more_vert</md-icon>
        </md-button>
      </div>
    </div>

    <div class="md-toolbar-row">
      <md-tabs class="md-primary">
        <md-tab id="tab-home" md-label="Predefined"></md-tab>
        <md-tab id="tab-pages" md-label="Annotate"></md-tab>
        <md-tab id="tab-posts" md-label="Explore"></md-tab>
      </md-tabs>
    </div>
  </div>
</template>

<script>
export default {
  name: "toolbar",
};
</script>

<style>

.span-window-horizontal {
  width: 97vw !important;
}

</style>