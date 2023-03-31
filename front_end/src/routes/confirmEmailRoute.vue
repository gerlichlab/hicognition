<template>

    <md-app md-waterfall md-mode="fixed-last">
        <md-app-toolbar class="md-large md-dense md-primary">
            <loginToolbar></loginToolbar>
        </md-app-toolbar>

        <md-app-content>
            <div class="spinner-container">
                <div style="height: 500px" v-if="showLoad">
                    <md-progress-spinner
                        :md-diameter="400"
                        :md-stroke="15"
                        md-mode="indeterminate"
                    ></md-progress-spinner>
                </div>
                <div>
                    <span class="md-display-1" v-if="showLoad">
                        Email is being confirmed!
                    </span>
                    <span class="md-display-1" v-else>
                        Something went wrong with confirmation!
                    </span>
                </div>
            </div>
        </md-app-content>
    </md-app>

</template>


<script>
import loginToolbar from "../components/ui/loginToolbar";
import { apiMixin } from "../mixins";

export default {
    name: "confirmEmail",
    components: {
        loginToolbar
    },
    mixins: [apiMixin],
    data: function() {
        return {
            showLoad: true,
            confirmationToken: null
        }
    },
    methods: {
        parseQueryString: function() {
            let queryObject = this.$route.query;
            if ("emailToken" in queryObject) {
                this.confirmationToken = queryObject["emailToken"];
                this.confirmEmail();
            }else{
                this.showLoad = false
            }
        },
        confirmEmail: function() {
            this.fetchData(`confirmation/${this.confirmationToken}/`).then(response => {
                if (response) {
                    // success
                    setTimeout(() => this.$router.push("/main/compare"), 1000)
                }else{
                    this.showLoad = false
                }
            })
        }

    },
    created: function() {
        this.parseQueryString();
    }
};
</script>

<style scoped>
.spinner-container {
    display: flex;
    justify-content: center;
    align-content: center;
    align-items: center;
    height: 800px;
    flex-direction: column;
}
</style>
