<template>
  <div>
    <md-table v-model="datasets" md-sort="dataset_name" md-sort-order="asc" md-fixed-header @md-selected="onSelect">

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
          <md-button class="md-icon-button">
            <md-icon>delete</md-icon>
          </md-button>
        </div>
      </md-table-toolbar>
      <!-- Empty state for table -->
      <md-table-empty-state
        md-label="No datasets found"
        :md-description="`No datasets found for this query. Try a different search term or create a new dataset.`">
      </md-table-empty-state>
      <!-- Definition of how table should look -->
      <md-table-row slot="md-table-row" slot-scope="{ item }" md-selectable="multiple" class="md-primary" md-auto-select>
        <md-table-cell md-label="Name" md-sort-by="dataset_name">{{ item.dataset_name }}</md-table-cell>
        <md-table-cell md-label="Filetype" md-sort-by="filetype">{{ item.filetype }}</md-table-cell>
        <md-table-cell md-label="HiGlass ID" md-sort-by="higlass_uuid">{{ item.higlass_uuid }}</md-table-cell>
        <md-table-cell md-label="Progress" md-sort-by="completed">
          <md-icon  v-if="item.processing_state == 'finished'">done</md-icon>
          <md-progress-spinner :md-diameter="30" md-mode="indeterminate" v-else-if="item.processing_state == 'processing'"></md-progress-spinner>
          <md-icon v-else-if="item.processing_state == 'failed'">error</md-icon>
          <md-icon v-else-if="item.processing_state == 'uploaded'">cloud_done</md-icon>
          <md-icon v-else-if="item.processing_state == 'uploading'">cloud_upload</md-icon>
        </md-table-cell>
      </md-table-row>
    </md-table>
  </div>
</template>

<script>
import { toLower, searchByName } from "../functions";
import { apiMixin } from "../mixins";

export default {
    name: 'datasetTable',
    mixins: [apiMixin],
    data: () => ({
      selected: []
    }),
    methods: {
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
            // success, store datasets
            this.$store.commit("setDatasets", response.data);
            });
      }
    },
    computed: {
      showDelete: function () {
        if (this.selected){
          return true;
        }
        return false;
      },
      datasets: function() {
          return this.$store.state.datasets; // initial getting from store
      }
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