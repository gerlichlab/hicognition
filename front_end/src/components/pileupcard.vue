<template>
  <md-card md-with-hover class="pileup-card">
    <md-card-content>
    
    <!-- Binsize submission form -->
      <div class="md-layout md-gutter" ref="pileup-card-element">
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
                :value="item.binsize"
                :key="item.binsize"
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
          >Submit</md-button
        >
      </div>
      <md-divider></md-divider>

      <!-- Pileup ICCF -->
      <pileup
        title="ICCF"
        pileupType="ICCF"
        pileupID="1"
        v-if="showPileup"
        :width="pileupDim"
        :height="pileupDim"
        :pileupData="pileupDataICCF"
        log="true"
      ></pileup>

      <md-divider
        class="md-inset"
        pileupType="ObsExp"
        v-if="showPileup"
      ></md-divider>

      <!-- Pileup Obs/Exp -->
      <pileup
        title="Obs/Exp"
        pileupType="ObsExp"
        v-if="showPileup"
        pileupID="2"
        :width="pileupDim"
        :height="pileupDim"
        :pileupData="pileupDataObsExp"
        log="true"
      ></pileup>


      <!-- Placeholder for empty state -->
      <md-empty-state
        md-icon="input"
        md-label="Add a dataset"
        md-description="Once you added a dataset to the higlass browser, you can explore it"
        class="fill-card"
        v-show="!showPileup"
      >
      </md-empty-state>
    </md-card-content>
  </md-card>
</template>

<script>
import pileup from "./pileup";
import { apiMixin } from "../mixins";

export default {
  name: "pileup-card",
  mixins: [apiMixin],
  components: {
    pileup,
  },
  data: function () {
    return {
      selectedBinsize: null,
      pileups: [], // pileups and their binsizes to display at the binsize selection
      blockSelection: true, // whether to show controls for binsize selection
      pileupDataICCF: null,
      pileupDataObsExp: null,
      pileupDim: 0, // Dimensions of pileup. Side lenght in pixels of the square the pileup is in.
    };
  },
  computed: {
    showPileup: function () {
      return this.pileupDataICCF && this.pileupDataObsExp;
    },
  },
  methods: {
    updatePileupSize: function () {
      // rescale pileups upon window resize
      var value = this.$refs["pileup-card-element"].offsetWidth * 0.45;
      this.pileupDim = value;
    },
    handleBinsizeSubmit: function () {
      // get ids from user selection
      var iccf_id = this.pileups[this.selectedBinsize]["ICCF"];
      var obs_exp_id = this.pileups[this.selectedBinsize]["Obs/Exp"];
      // get pileup iccf; update pileup data upon success
      this.fetchData(`pileups/data/${iccf_id}/`).then((response) => {
        this.pileupDataICCF = JSON.parse(response.data);
      });
      // get pileup obs/exp; update pileup data upon success
      this.fetchData(`pileups/data/${obs_exp_id}/`).then((response) => {
        this.pileupDataObsExp = JSON.parse(response.data);
      });
    },
  },
  watch: {
    "$store.state.predefined.datasetSelection": function (value) {
      // watches storing of dataset selection in store
      if (value) {
        // unpack  values
        var { cooler_id, bedpe_id } = value;
        // fetch pileup datasets and display binsizes
        this.fetchData(`pileups/${cooler_id}/${bedpe_id}/`).then((response) => {
          // success, store datasets in predefined store
          this.$store.commit("predefined/setPileups", response.data);
          // update binsizes to show
          // Each dataset will have iccf and obs/exp data, therefore I
          // make a new array with [{ "ICCF": iccf_id, "Obs/Exp": obs_exp_id, "binsize": binsize}]
          // TODO: Refactor into a function!
          var numberDatasets = response.data.length;
          var iccfObsExpStratified = {};
          for (var index = 0; index < numberDatasets; index++) {
            var { id, binsize, value_type } = response.data[index];
            if (binsize in iccfObsExpStratified) {
              iccfObsExpStratified[binsize][value_type] = id;
            } else {
              iccfObsExpStratified[binsize] = { binsize: binsize };
              iccfObsExpStratified[binsize][value_type] = id;
            }
          }
          this.pileups = iccfObsExpStratified;
          // show controls
          this.blockSelection = false;
          // reset selection
          this.selectedBinsize = null;
        });
      }
    },
  },
  mounted: function () {
    // add resize event listener and seed initial value
    // TODO: this does not work, fix it!
    this.updatePileupSize();
    window.addEventListener("resize", this.updatePileupSize);
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