<template>
    <md-app md-waterfall md-mode="fixed-last">
        <md-app-toolbar class="md-large md-dense md-primary">
            <loginToolbar></loginToolbar>
        </md-app-toolbar>

        <md-app-content>
            <loginForm></loginForm>
        </md-app-content>
    </md-app>
</template>

<script>
import loginToolbar from "../components/ui/loginToolbar";
import loginForm from "../components/forms/loginForm";

export default {
    name: "Login",
    components: {
        loginToolbar,
        loginForm
    },
    mounted: function(){
        // check if token is there and push to main route
        if (!this.$store.getters.isTokenEmpty){
            this.$router.push("/main/compare");
        }
    }

};
</script>

<style scoped>
.halfwidth {
    width: 20vw;
    height: 35v;
}

.center {
    margin: 0;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
</style>
