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
import {version} from '../../package.json'
export default {
  name: "loginToolbar",
  appversion: version,
};
//TODO: Version is not working.
</script>

<style>

.span-window-horizontal {
  width: 97vw !important;
}

</style>