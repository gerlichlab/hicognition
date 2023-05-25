<template>
    <md-app md-waterfall md-mode="fixed-last">
        <md-app-toolbar class="md-large md-dense md-primary">
            <loginToolbar></loginToolbar>
        </md-app-toolbar>

        <md-app-content>
            <registrationForm></registrationForm>
        </md-app-content>
    </md-app>
</template>

<script>
import loginToolbar from "../components/ui/loginToolbar";
import registrationForm from "../components/forms/registrationForm";

export default {
    name: "Register",
    components: {
        loginToolbar,
        registrationForm
    },
    mounted: function() {
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
