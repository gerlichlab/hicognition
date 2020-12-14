<template>
  <md-card md-with-hover class="higlass-card">
    <md-card-content>
      <!-- Cooler/Region/Windowsize selection form -->
      <div class="md-layout md-gutter">
        <!-- Refresh button -->
        <md-button
          class="md-dense md-raised button-margin md-primary md-icon-button"
          @click="fetchDatasets"
        >
          <md-icon>cached</md-icon>
        </md-button>
        <!-- Cooler selection field -->
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
        <!-- Region selection field -->
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
        <!-- Windowsize selection field -->
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
        <!-- Submit button -->
        <md-button
          class="md-dense md-raised button-margin"
          md-menu-trigger
          @click="handleDatasetSubmit"
          :disabled="blockSubmit"
          >Submit</md-button
        >
      </div>
      <md-divider></md-divider>
      <!-- Empty state placeholder -->
      <div v-show="showEmpty">
        <md-empty-state
          md-icon="input"
          md-label="Add a dataset"
          md-description="Once you added a dataset to the higlass browser, you can explore it"
          class="fill-card"
        >
        </md-empty-state>
      </div>
      <!-- Higlass browser -->
      <div
        id="higlass-browser"
        :class="higlassClass"
        ref="higlass-browser"
      ></div>
    </md-card-content>
  </md-card>
</template>

<script>
import {
  getDefaultViewConf,
  getEmptyConf,
  cunstructViewConf,
  constructViewConf,
} from "../functions";
import { apiMixin } from "../mixins";

export default {
  name: "higlass-card",
  mixins: [apiMixin],
  data: function () {
    return {
      higlass: null,
      showEmpty: true,
      higlassClass: [""], // higlassClass is needed to be able to mark appearance of higlass by just increasing the size of the initial div
      selectedCoolerID: null,
      selectedRegionID: null,
      selectedBedPeID: null,
      coolers: [],
      bedfiles: [],
      bedpeFiles: [],
      blockWindowsize: true, // only show windowsizes after bedperegions are there
    };
  },
  computed: {
    blockSubmit: function () {
      if (this.selectedCoolerID && this.selectedRegionID && this.selectedBedPeID){
        return false
      }
      return true
    },
    selectedCooler: function () {
      if (!this.selectedCoolerID) {
        return null;
      }
      return this.coolers.filter((element) => {
        return element.id == this.selectedCoolerID;
      })[0]; // filter returns array [coolerJson], but I need the object
    },
    selectedRegion: function () {
      if (!this.selectedRegionID) {
        return null;
      }
      return this.bedfiles.filter((element) => {
        return element.id == this.selectedRegionID;
      })[0]; // filter returns array [bedJson], but I need the object
    },
    selectedBedPe: function () {
      if (!this.selectedBedPeID) {
        return null;
      }
      return this.bedpeFiles.filter((element) => {
        return element.id == this.selectedBedPeID;
      })[0]; // filter returns array [bedPeJson], but I need the object
    },
    viewConf: function () {
      return constructViewConf(
        this.selectedCooler,
        this.selectedRegion,
        this.selectedBedPe
      );
    },
  },
  methods: {
    handleDatasetSubmit: function () {
      if (this.higlass) {
        // higlass exists already, update dataset
        this.higlass.setViewConfig(this.viewConf);
      } else {
        /*
          higlass does not exist, create it
          add fill card to higlass class. This is a hack because the
          react based higlass viewer does not render with the
          v-if or v-show directives
        */
        this.showEmpty = false;
        this.higlassClass.push("fill-card");
        // swtiched on, update higlass
        this.createHiGlass();
      }
      // add current selection to vuex-store so other parts of the app have access
      var selection = {
        cooler_id: this.selectedCoolerID,
        region_id: this.selectedRegionID,
        bedpe_id: this.selectedBedPeID,
      };
      this.$store.commit("predefined/setDatasetSelection", selection);
    },
    fetchPileupregions: function () {
      this.fetchData(`datasets/${this.selectedRegionID}/pileupregions/`).then(
        (response) => {
          // success, store datasets
          this.$store.commit("predefined/setPileupRegions", response.data);
          this.bedpeFiles = response.data;
          this.blockWindowsize = false;
        }
      );
    },
    createHiGlass: function () {
      this.higlass = hglib.viewer(
        document.getElementById("higlass-browser"),
        this.viewConf,
        {
          bounded: true,
          editable: false,
        }
      );
    },
    fetchDatasets: function () {
      this.fetchData("datasets/").then((response) => {
        // success, store datasets
        this.$store.commit("setDatasets", response.data);
        // update datasets; Only use completed datasets; completed is 1 if completed, 0 if in progress and -1 if failed
        this.coolers = response.data.filter(
          (element) => element.filetype == "cooler" && (element.processing_state == "finished")
        );
        this.bedfiles = response.data.filter(
          (element) => element.filetype == "bedfile" && (element.processing_state == "finished")
        );
      });
    },
  },
  watch: {
    selectedRegionID: function () {
      this.fetchPileupregions();
      // clear selected pileupregions
      this.selectedBedPeID = null;
    },
  },
  created: function () {
    this.fetchDatasets();
  },
};
</script>


<style lang="scss" scoped>
.higlass-card {
  width: 65vw;
  height: calc(100vh - 100px);
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