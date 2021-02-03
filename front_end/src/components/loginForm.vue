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
        <md-button class="md-dense md-raised md-primary" @click="handleSubmit"
          >Submit</md-button
        >
        <div v-if="showError" class="red floatright">Wrong Credentials!</div>
      </md-card-content>
    </md-card>
  </div>
</template>

<script>
import { apiMixin } from "../mixins";

export default {
  name: "Login",
  mixins: [apiMixin],
  data: function () {
    return {
      username: "",
      password: "",
      showError: false,
    };
  },
  methods: {
    handleSubmit: function () {
      if (this.password.length > 0) {
        this.fetchAndStoreToken(this.username, this.password)
          .then(() => {
            //fetching and storing in store worked, redirect to main/predefined
            this.$router.push("/main/compare");
          })
          .catch((error) => {
            // something went wrong
            console.log(error);
            this.showError = true;
          });
      }
    },
  },
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