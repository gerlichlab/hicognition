<template>
<b-container>
    <b-row fluid class="flex-grow-1 d-flex align-items-center justify-content-center">
        <b-col></b-col>
        <b-col  md="6" lg="4" cols="5">
            <b-card no-body>
                <b-card-header>
                    <h4 class="mb-0">Login</h4>
                </b-card-header>
                <b-card-body>
                    <b-form-group label="Username">
                    <b-form-input v-model="username"></b-form-input>
                    </b-form-group>
                    <b-form-group label="Password">
                    <b-form-input v-model="password" type="password"></b-form-input>
                    </b-form-group>
                    <b-button variant="primary" class="mr-3" @click="handleSubmit">Login</b-button>
                    <b-button variant="secondary" @click="$router.push('register/')">Register</b-button>
                    <div v-if="showError" class="text-danger float-right">
                    Wrong Credentials!
                    </div>
                </b-card-body>
            </b-card>
        </b-col>
        <b-col></b-col>
    </b-row>
</b-container>
</template>

<script>
import { apiMixin } from "../../mixins";

export default {
  name: "LoginForm",
  mixins: [apiMixin],
  data: function () {
    return {
      username: "",
      password: "",
      showError: false,
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
  },
};
</script>

<style scoped>

.min-width-card {
  min-width: 300px;
}

.full-screen {
  width: 100vw;
  height: 100vh;
}

.float-right {
  float: right;
}

.fill-remaining-space {
  flex: 1 1
}

</style>