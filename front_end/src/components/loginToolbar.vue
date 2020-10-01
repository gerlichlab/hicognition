<template>
  <div>
    <!-- span window horizontal is needed to position logout on the right -->
    <div class="md-toolbar-row span-window-horizontal">
      <div class="md-toolbar-section-start">
        <span class="md-title">HiCognition 0.1</span>
      </div>

      <div class="md-toolbar-section-end">
        <md-button class="md-icon-button">
          <md-icon>more_vert</md-icon>
        </md-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "loginToolbar",
};
</script>

<style>

.span-window-horizontal {
  width: 97vw !important;
}

</style>