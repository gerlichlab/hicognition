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
      pileups: [],
      blockSelection: true // control whether to show controls for binsize selection
    }
  },
  methods: {
    handleBinsizeSubmit: function () {
      return
    }
  },
  watch: {
    '$store.state.datasetSelectionPredefined': function(value) {
      // watches storing of dataset selection in store
      if (value) {
          // unpack  values
          var { cooler_id, bedpe_id } = value;
          // fetch pileup datasets and display binsizes
          var token = this.$store.state.token;
          var encodedToken = btoa(token + ":");
          this.$http
            .get(process.env.API_URL + `pileups/${cooler_id}/${bedpe_id}/`, {
              headers: {
                Authorization: `Basic ${encodedToken}`,
              },
            })
            .then((response) => {
              if (response.status != 200) {
                console.log(`Error: ${response.data}`);
              } else {
                // success, store datasets
                this.$store.commit("setPileups", response.data);
                // update binsizes to show
                this.pileups = response.data;
                // show controls
                this.blockSelection = false;
                // reset selection
                this.selectedBinsize = null;
              }
        });
      }
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