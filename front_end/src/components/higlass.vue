<template>
  <md-card md-with-hover class="higlass-card">
    <md-card-content>

      <div class="md-layout md-gutter">

        <md-button class="md-dense md-raised button-margin md-primary md-icon-button" @click="getDatasets">
          <md-icon>cached</md-icon>
        </md-button>

        <div class="md-layout-item md-size-20">
          <md-field>
            <label for="cooler">Cooler</label>
            <md-select
              v-model="selectedCoolerID"
              name="cooler"
              id="cooler"
              placeholder="Cooler"
            >
              <md-option
                v-for="item in coolers"
                :value="item.id"
                :key="item.id"
                >{{ item.dataset_name }}</md-option
              >
            </md-select>
          </md-field>
        </div>

        <div class="md-layout-item md-size-20">
          <md-field>
            <label for="region">Region</label>
            <md-select
              v-model="selectedRegionID"
              name="region"
              id="region"
              placeholder="Regions"
            >
              <md-option
                v-for="item in bedfiles"
                :value="item.id"
                :key="item.id"
                >{{ item.dataset_name }}</md-option
              >
            </md-select>
          </md-field>
        </div>

        <div class="md-layout-item md-size-20">
          <md-field>
            <label for="bedpe">Windowsize</label>
            <md-select
              v-model="selectedBedPeID"
              name="bedpe"
              id="bedpe"
              placeholder="Windowsize"
              :disabled="blockWindowsize"
            >
              <md-option
                v-for="item in bedpeFiles"
                :value="item.id"
                :key="item.id"
                >{{ item.windowsize }}</md-option
              >
            </md-select>
          </md-field>
        </div>

        <md-button
          class="md-dense md-raised button-margin"
          md-menu-trigger
          @click="handleDatasetSubmit"
          :disabled="blockWindowsize"
          >Submit</md-button
        >
      </div>

      <md-divider></md-divider>
      <div v-show="showEmpty">
        <md-empty-state
          md-icon="input"
          md-label="Add a dataset"
          md-description="Once you added a dataset to the higlass browser, you can explore it"
          class="fill-card"
        >
        </md-empty-state>
      </div>
      <div
        id="higlass-browser"
        :class="higlassClass"
        ref="higlass-browser"
      ></div>
    </md-card-content>
  </md-card>
</template>

<script>
import { getDefaultViewConf, getEmptyConf, cunstructViewConf, constructViewConf } from "../functions";

export default {
  name: "higlass-card",
  data: function () {
    return {
      higlass: null,
      showEmpty: true,
      higlassClass: [""],
      selectedCoolerID: null,
      selectedRegionID: null,
      selectedBedPeID: null,
      coolers: [],
      bedfiles: [],
      bedpeFiles: [],
      blockWindowsize: true // only show this after bedperegions are there
    };
  },
  computed: {
    selectedCooler: function () {
      if (!this.selectedCoolerID){
        return null;
      }
      return this.coolers.filter( element => {
        return element.id == this.selectedCoolerID
      })[0] // return only the object at position 0
    },
    selectedRegion: function () {
      if (!this.selectedRegionID){
        return null;
      }
      return this.bedfiles.filter( element => {
        return element.id == this.selectedRegionID
      })[0] // return only the object at position 0
    },
    selectedBedPe: function () {
      if (!this.selectedBedPeID) {
        return null;
      }
      return this.bedpeFiles.filter( element => {
        return element.id == this.selectedBedPeID
      })[0] // return only the object at position 0
    },
    viewConf: function() {
      return constructViewConf(
            this.selectedCooler,
            this.selectedRegion,
            this.selectedBedPe
        );
    }
  },
  methods: {
    handleDatasetSubmit: function () {
      if (this.higlass){
        // higlass exists already, update dataset
        this.higlass.setViewConfig(this.viewConf);
      }else{
        // higlass does not exist, create it
        // add fill card to higlass class. This is a hack because the
        // react based higlass viewer does not render with the
        // v-if or v-show directives
        this.showEmpty = false;
        this.higlassClass.push("fill-card");
        // swtiched on, update higlass after DOM update
        this.createHiGlass();
      }
      // add current selection to vuex-store so other parts of the app have access
      var selection = {
        cooler_id: this.selectedCoolerID,
        region_id: this.selectedRegionID,
        bedpe_id: this.selectedBedPeID
      }
      this.$store.commit("predefined/setDatasetSelection", selection);
    },
    fetchPileupregions: function () {
        var token = this.$store.state.token;
        var encodedToken = btoa(token + ":")
        this.$http.get(process.env.API_URL + `datasets/${this.selectedRegionID}/pileupregions/`, {
          headers: {
            "Authorization": `Basic ${encodedToken}`
          }
        }).then(response => {
          if (response.status != 200){
            console.log(`Error: ${response.data}`);
          }else{
            // success, store datasets
            this.$store.commit("predefined/setPileupRegions", response.data);
            this.bedpeFiles = response.data;
            this.blockWindowsize = false;
          }
        })
    },
    createHiGlass: function () {
      this.higlass = hglib.viewer(
        document.getElementById("higlass-browser"),
        this.viewConf,
        {
          bounded: true,
          editable: false
        }
      );
    },
    getDatasets: async function () {
      var token = this.$store.state.token;
      var encodedToken = btoa(token + ":");
      this.$http
        .get(process.env.API_URL + "datasets/", {
          headers: {
            Authorization: `Basic ${encodedToken}`,
          },
        })
        .then((response) => {
          if (response.status != 200) {
            console.log(`Error: ${response.data}`);
          } else {
            // success, store datasets
            this.$store.commit("setDatasets", response.data);
            // update datasets
            this.coolers = response.data.filter(
              (element) => element.filetype == "cooler" && element.completed
            );
            this.bedfiles = response.data.filter(
              (element) => element.filetype == "bedfile" && element.completed
            );
          }
        });
    }
  },
  watch: {
    selectedRegionID: function () {
      this.fetchPileupregions();
      // clear selected pileupregions
      this.selectedBedPeID = null;
    }
  },
  created: function () {
    this.getDatasets();
  },
};
</script>


<style lang="scss" scoped>
.higlass-card {
  width: 65vw;
  height: 88vh;
  margin: 4px;
  display: inline-block;
  vertical-align: top;
}

.fill-card {
  width: 100%;
  height: 78vh;
}

.button-margin {
  margin: 24px;
}
</style>