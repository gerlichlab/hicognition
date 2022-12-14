<template>
    <md-app md-waterfall md-mode="fixed-last">
        <md-app-toolbar class="md-large md-dense md-primary">
            <loginToolbar></loginToolbar>
        </md-app-toolbar>

        <md-app-content>
            <md-empty-state
                md-icon="devices_other"
                md-label="Confirm your email"
                md-description="After you have confirmed your E-mail you can start exploring!">
                <div>
                    <md-button @click="resendEmail" class="md-primary md-raised">Resend Email</md-button>
                    <md-button  @click="logout" class="md-secondary md-raised">Logout</md-button>
                </div>
            </md-empty-state>
        </md-app-content>
        <md-snackbar :md-active.sync="showSnackbar"
            >Email sent!</md-snackbar
        >
    </md-app>
</template>

<script>
import loginToolbar from "../components/ui/loginToolbar";
import { apiMixin } from "../mixins";

export default {
    name: "resendEmail",
    components: {
        loginToolbar
    },
    mixins: [apiMixin],
    data: function() {
        return {
            showSnackbar: false
        }
    },
    methods: {
        logout: function() {
            this.$store.commit("clearToken");
            this.$store.commit("clearSessionToken");
            this.$globalFlags["serializeCompare"] = false;
            this.$store.commit("compare/clearAll");
            this.$router.push("/login");
        },
        resendEmail: function() {
            this.fetchData("resend/").then(response => {
                // success, store datasets
                if (response) {
                    this.showSnackbar = true
                    setTimeout(() => this.logout(), 1000)
                }
            });
        }
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
