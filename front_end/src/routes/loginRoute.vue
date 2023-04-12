<template>
  <div class="fill-viewport-height flex-box">
    <b-navbar toggleable="lg" variant="primary" class="sticky-top">
      <login-toolbar></login-toolbar>
    </b-navbar>

    <b-container class="d-flex justify-content-center align-items-center fill-remaining-height">
      <login-form></login-form>
    </b-container>
  </div>
</template>

<script>
import loginToolbar from "../components/ui/loginToolbar";
import loginForm from "../components/forms/loginForm";

export default {
  name: "Login",
  components: {
    loginToolbar,
    loginForm,
  },
  mounted: function () {
    // check if token is there and push to main route
    if (!this.$store.getters.isTokenEmpty) {
      this.$router.push("/main/compare");
    }
  },
};
</script>

<style scoped>

.fill-viewport-height {
  height: 100vh;
}

.flex-box {
  display: flex;
  flex-direction: column;
}

.fill-remaining-height {
  flex-grow: 1;
}

</style>
