<template>
  <md-card md-with-hover class="pileup-card">
    <md-card-header>
      <div class="md-title">Pileup</div>
    </md-card-header>

    <md-card-content class="pileup-content">
      <pileup title="ICCF"></pileup>

      <pileup title="Obs/Exp"></pileup>
    </md-card-content>
  </md-card>
</template>

<script>
import pileup from "./pileup";

export default {
  name: "pileup-card",
  components: {
    pileup,
  },
};
</script>

<style lang="scss" scoped>
.pileup-card {
  width: 30vw;
  height: 88vh;
  margin: 4px;
  display: inline-block;
}

.pileup-content {
  height: 95%;
}
</style>