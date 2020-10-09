<template>
  <md-card md-with-hover class="higlass-card">
    <md-card-content>
      <div class="md-layout md-gutter">
        <div class="md-layout-item md-size-20">
          <md-field>
            <label for="cooler">Cooler</label>
            <md-select
              v-model="selectedCoolerID"
              name="cooler"
              id="cooler"
              placeholder="Cooler"
              @click="updateDatasetSelection"
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
              @click="updateDatasetSelection"
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

        <md-button
          class="md-dense md-raised button-margin"
          md-menu-trigger
          @click="handleDatasetSubmit"
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
      // TODO: api call for pileupregions
      return null;
    }
  },
  methods: {
    handleDatasetSubmit () {
      if (this.higlass){
        // higlass exists already, destroy and recreate
        this.higlass.destroy()
        this.createHiGlass()
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
    },
    createHiGlass: function () {
      var viewconf =  constructViewConf(
        this.selectedCooler,
        this.selectedRegion,
        this.selectedBedPe
      );
      console.log(viewconf);
      this.higlass = hglib.viewer(
        document.getElementById("higlass-browser"),
        viewconf,
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
    },
    updateDatasetSelection: function () {
      var datasets = this.$store.state.datasets;
      this.coolers = datasets.filter(
        (element) => element.filetype == "cooler" && element.completed
      );
      this.bedfiles = datasets.filter(
        (element) => element.filetype == "bedfile" && element.completed
      );
    },
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