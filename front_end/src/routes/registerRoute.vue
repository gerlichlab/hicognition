<template>
  <div class="fill-viewport-height flex-box">
    <b-navbar toggleable="lg" variant="primary" class="sticky-top">
      <login-toolbar></login-toolbar>
    </b-navbar>

    <b-container class="d-flex justify-content-center align-items-center fill-remaining-height">
      <registrationForm></registrationForm>
    </b-container>
  </div>
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
