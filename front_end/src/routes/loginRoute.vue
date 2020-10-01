<template>
  <div>

  <md-card md-with-hover class="halfwidth center">
    <md-card-header>
      <div class="md-title">Login</div>
    </md-card-header>

    <md-card-content>
        <md-field md-clearable>
        <label>Username</label>
        <label>Username</label>
        <md-input v-model="initial"></md-input>
        </md-field>

        <md-field>
        <label>Password</label>
        <md-input v-model="password" type="password"></md-input>
        </md-field>
        <md-button class="md-dense md-raised md-primary">Submit</md-button>
    </md-card-content>
  </md-card>
  </div>
</template>

<script>
export default {
    name: 'Login',
    props: [
        "initial",
        "password"
    ]
}
</script>>

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

</style>>