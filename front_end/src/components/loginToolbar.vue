<template>
  <div>
    <!-- span window horizontal is needed to position logout on the right -->
    <div class="md-toolbar-row span-window-horizontal">
      <div class="md-toolbar-section-start">
        <span class="md-title">HiCognition {{appversion}}</span>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: "loginToolbar",
  data: function () {
    return {
      appversion: process.env.VERSION
    }
  },
  created () {
    console.log(process.env);
  }
};
</script>

<style>

.span-window-horizontal {
  width: 97vw !important;
}

</style>