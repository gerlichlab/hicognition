<template>
    <div class="page-container">
        <router-view></router-view>
    </div>
</template>

<script>
import router_default from "./router";
import router_showcase from "./routerShowcase";

// TODO: THis does not seem to work
//var showcase_bool = process.env.SHOWCASE

//const router = !showcase_bool ? router_default : router_showcase

export default {
    name: "mainApp",
    router: !process.env.SHOWCASE ? router_default : router_showcase,
};
</script>

<style lang="scss" scoped>
.md-app {
    height: 100vh;
    border: 1px solid rgba(#000, 0.12);
}
</style>
