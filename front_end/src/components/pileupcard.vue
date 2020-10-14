<template>
  <md-card md-with-hover class="pileup-card">
    <md-card-content>
      <div class="md-layout md-gutter">
        <div class="md-layout-item md-size-20">
          <md-field>
            <label for="binsize">Binsize</label>
            <md-select
              v-model="selectedBinsize"
              name="binsize"
              id="binsize"
              placeholder="Binsize"
              @click="updateDatasetSelection"
              :disabled="blockSelection"
            >
              <md-option
                v-for="item in pileups"
                :value="item.id"
                :key="item.id"
                >{{ item.binsize }}</md-option
              >
            </md-select>
          </md-field>
        </div>

        <md-button
          class="md-dense md-raised button-margin"
          md-menu-trigger
          @click="handleBinsizeSubmit"
          :disabled="blockSelection"
          >Submit</md-button>
        </div>
    <md-divider></md-divider>
      <pileup title="ICCF" v-show="showPileup"></pileup>
      <pileup title="Obs/Exp" v-show="showPileup"></pileup>
        <md-empty-state
          md-icon="input"
          md-label="Add a dataset"
          md-description="Once you added a dataset to the higlass browser, you can explore it"
          class="fill-card"
          v-show="!showPileup">
        </md-empty-state>
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
  data: function () {
    return {
      showPileup: false,
      selectedBinsize: null,
      blockSelection: true // control whether to show controls for binsize selection
    }
  },
  methods: {
    handleBinsizeSubmit: function () {
      return
    }
  }
};
</script>

<style lang="scss" scoped>
.pileup-card {
  width: 30vw;
  height: 88vh;
  margin: 4px;
  display: inline-block;
}

/* .pileup-content {
  height: 95%;
} */

.fill-card {
  width: 100%;
  height: 78vh;
}

.button-margin {
  margin: 24px;
}

</style>