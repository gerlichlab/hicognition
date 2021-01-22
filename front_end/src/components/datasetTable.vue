<template>
  <div>
    <md-table v-model="datasets" md-sort="dataset_name" md-sort-order="asc" md-card md-fixed-header @md-selected="onSelect">

      <!-- Table toolbar has the update button and the search field -->
      <md-table-toolbar>
        <!-- Update button -->
        <div class="md-toolbar-section-start">
            <md-button class="md-dense md-raised button-margin md-primary md-icon-button" @click="fetchDatasets">
              <md-icon>cached</md-icon>
            </md-button>
        </div>
      </md-table-toolbar>

      <md-table-toolbar slot="md-table-alternate-header" slot-scope="{ count }">
        <div class="md-toolbar-section-start">{{ getAlternateLabel(count) }}</div>

        <div class="md-toolbar-section-end">
          <md-button class="md-icon-button" @click="deleteClicked" v-if="!clickedDelete">
            <md-icon>delete</md-icon>
          </md-button>
          <md-button class="md-raised" v-if="clickedDelete">
              Are you sure?
          </md-button>
          <md-button class="md-raised md-accent" v-if="clickedDelete" @click="handleDelete">
              Yes
          </md-button>
          <md-button class="md-raised md-primary" v-if="clickedDelete" @click="clickedDelete = false">
              No
          </md-button>
        </div>
      </md-table-toolbar>
      <!-- Empty state for table -->
      <md-table-empty-state
        md-label="No datasets found"
        :md-description="`No datasets found for this query. Try a different search term or create a new dataset.`">
      </md-table-empty-state>
      <!-- Definition of how table should look -->
      <md-table-row slot="md-table-row" slot-scope="{ item }" md-selectable="multiple" class="md-primary" md-auto-select :md-disabled="anyProcessing">
        <md-table-cell md-label="Name" md-sort-by="dataset_name">{{ item.dataset_name }}</md-table-cell>
        <md-table-cell md-label="Filetype" md-sort-by="filetype">{{ item.filetype }}</md-table-cell>
        <md-table-cell md-label="Genotype" md-sort-by="genotype">{{ item.genotype }}</md-table-cell>
        <md-table-cell md-label="Description" md-sort-by="description">{{ item.description }}</md-table-cell>
        <md-table-cell md-label="Progress" md-sort-by="processing_state">
          <md-icon  v-if="item.processing_state == 'finished'">done</md-icon>
          <md-progress-spinner :md-diameter="30" md-mode="indeterminate" v-else-if="item.processing_state == 'processing'"></md-progress-spinner>
          <md-icon v-else-if="item.processing_state == 'failed'">error</md-icon>
          <md-icon v-else-if="item.processing_state == 'uploaded'">cloud_done</md-icon>
          <md-icon v-else-if="item.processing_state == 'uploading'">cloud_upload</md-icon>
        </md-table-cell>
      </md-table-row>
    </md-table>
    <md-snackbar :md-active.sync="datasetsDeleted"
      >Deletion done!</md-snackbar
    >
  </div>
</template>

<script>

import { apiMixin } from "../mixins";

export default {
    name: 'datasetTable',
    mixins: [apiMixin],
    data: () => ({
      selected: [],
      datasets: [],
      clickedDelete: false,
      datasetsDeleted: false
    }),
    methods: {
      deleteClicked: function () {
        this.clickedDelete = true;
      },
      handleDelete: async function() {
        this.clickedDelete = false;
        for (var dataset of this.selected){
          var result = await this.deleteData(`datasets/${dataset.id}/`);
        }
        this.datasetsDeleted = true;
        this.selected = [];
        this.fetchDatasets();
      },
      getAlternateLabel (count) {
        let plural = ''

        if (count > 1) {
          plural = 's'
        }

        return `${count} data set${plural} selected`
      },
      onSelect (item) {
        this.selected = item
      },
      fetchDatasets() {
        this.fetchData("datasets/")
            .then(response => {
              if (response){
                // success, store datasets
                this.$store.commit("setDatasets", response.data);
                // update displayed datasets
                this.datasets = response.data;
              }
            });
      }
    },
    computed: {
      anyProcessing: function () {
        for (var dataset of this.datasets){
          if (dataset.processing_state == "processing"){
            return true;
          }
        }
        return false;
      },
      showDelete: function () {
        if (this.selected.length != 0){
          return true;
        }
        return false;
      }
    },
    created: function () {
      this.datasets = this.$store.state.datasets;
    }
  }
</script>

<style lang="scss" scoped>
  .md-field {
    max-width: 200px;
  }
  .md-table {
    max-width: 90vw;
    min-width: 40vw;
  }
  .md-table-cell {
    text-align: center;
  }
</style>