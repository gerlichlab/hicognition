<template>
    <div>
        <md-card md-with-hover class="halfwidth center">
            <md-card-header>
                <div class="md-title">Login</div>
            </md-card-header>

            <md-card-content>
                <md-field md-clearable>
                    <label>Username</label>
                    <md-input v-model="username"></md-input>
                </md-field>

                <md-field>
                    <label>Password</label>
                    <md-input v-model="password" type="password"></md-input>
                </md-field>
                <md-button
                    class="md-dense md-raised md-primary"
                    @click="handleSubmit"
                    >Submit</md-button
                >
                <div v-if="showError" class="red floatright">
                    Wrong Credentials!
                </div>
            </md-card-content>
        </md-card>
        <md-card md-with-hover class="halfwidth">
            <md-card-header class="md-primary">
                <div class="md-title">New here?</div>
                <div class="md-subhead">
                    Check out our documentation and register
                </div>
            </md-card-header>
            <md-card-content class="md-layout">
                <div class="md-layout-item">
                    <md-button
                        class="md-dense md-raised md-secondary"
                        href="https://app.hicognition.com/docs/"
                        >Documentation</md-button
                    >
                </div>
                <div class="md-layout-item">
                    <md-button
                        class="md-dense md-raised md-secondary"
                        @click="$router.push('register/')"
                        >Register</md-button
                    >
                </div>
                <!--TODO fix doc ref-->
            </md-card-content>
        </md-card>
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";

export default {
    name: "LoginForm",
    mixins: [apiMixin],
    data: function() {
        return {
            username: "",
            password: "",
            showError: false
        };
    },
    methods: {
        handleSubmit: function() {
            if (this.password.length > 0) {
                this.fetchAndStoreToken(this.username, this.password)
                    .then(() => {
                        //fetching and storing in store worked, redirect either to main/compare or to next url
                        this.$globalFlags["serializeCompare"] = true;
                        if (this.$route.query && this.$route.query.redirect) {
                            this.$router.push(this.$route.query.redirect);
                        } else {
                            this.$router.push("/main/compare");
                        }
                    })
                    .catch(error => {
                        // something went wrong
                        console.log(error);
                        this.showError = true;
                    });
            }
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

.red {
    color: red;
}

.floatright {
    float: right;
}
</style>
