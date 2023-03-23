<template>
    <div class="page-container">
        <router-view></router-view>
    </div>
</template>

<script>
import router_default from "./router";

export default {
    name: "mainApp",
    router: router_default
};
</script>

<style lang="scss" scoped>
.md-app {
    height: 100vh;
    border: 1px solid rgba(#000, 0.12);
}
</style>
