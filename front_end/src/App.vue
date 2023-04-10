<template>
    <b-container class="fixed-container" fluid>
            <router-view></router-view>
    </b-container>
</template>

<script>
import router_default from "./router";
import router_showcase from "./routerShowcase";
import { BContainer } from "bootstrap-vue";

// TODO: THis does not seem to work
//var showcase_bool = process.env.SHOWCASE

//const router = !showcase_bool ? router_default : router_showcase

export default {
    name: "mainApp",
    components: {
        BContainer
    },
    router: !process.env.SHOWCASE ? router_default : router_showcase
};
</script>

<style>
.fixed-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto; /* Enable scrolling if content overflows */
  display: flex;
  flex-direction: column;
  margin: 0px;
  padding: 0px;
  height: 100vh;
}
</style>