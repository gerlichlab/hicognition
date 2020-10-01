<template>
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
        <md-button class="md-dense md-raised md-primary">Submit</md-button>
    </md-card-content>
  </md-card>
</template>

<script>

export default {
    name: 'Login',
    data: function () {
        return {
          username: "",
          password: ""
        }
    },
    methods: {
      handleSubmit: function (e) {
        e.preventDefault();
        if (this.password.length > 0) {
                    this.$http.post('http://localhost:5000/login', {
                        email: this.email,
                        password: this.password
                    })
                    .then(response => {
                      if (response){
                        //TODO: check status code
                      }
                    })
                    .catch(function (error) {
                        console.error(error.response);
                    });
          }
      }
    }
}
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