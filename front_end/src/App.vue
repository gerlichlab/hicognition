<template>
  <div class="page-container">
      <router-view></router-view>
  </div>
</template>

<script>

import router from "./router"

export default {
  name: "mainApp",
  router
};
</script>

<style lang="scss" scoped>
.md-app {
  height: 100vh;
  border: 1px solid rgba(#000, 0.12);
}
</style>