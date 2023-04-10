<template>
<b-container>
    <b-row fluid class="flex-grow-1 d-flex align-items-center justify-content-center">
        <b-col></b-col>
        <b-col  md="6" lg="4" cols="5">
          <b-form @submit="handleSubmit">
            <b-card no-body>
                <b-card-header>
                    <h4 class="mb-0">Login</h4>
                </b-card-header>
                <b-card-body>
                    <b-form-group label="Username" label-for='username' :invalid-feedback="invalidFeedback">
                      <b-form-input id='username' v-model="username" :state="validationState" required></b-form-input>
                    </b-form-group>
                    <b-form-group label="Password" :invalid-feedback="invalidFeedback">
                    <b-form-input v-model="password" type="password" :state="validationState" required></b-form-input>
                    </b-form-group>
                </b-card-body>


                <b-card-footer>
                    <b-row align-h="between" align-v="center">
                      <b-col cols="4">
                          <b-button variant="primary" class="mr-3" type='submit'>Login</b-button>
                      </b-col>
                      <b-col cols="4">
                        <b-link variant="outline-dark" @click="$router.push('register/')">Register</b-link>
                      </b-col>
                    </b-row>
                </b-card-footer>
            </b-card>
          </b-form>
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
  computed: {
    invalidFeedback: function () {
      if (this.showError) {
        return "Invalid username or password";
      }
      return "";
    },
    validationState: function () {
      if (this.showError) {
        return false;
      }
      return null;
    },
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