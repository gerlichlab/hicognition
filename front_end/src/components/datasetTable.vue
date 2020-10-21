<template>
  <div>
    <md-table v-model="searched" md-sort="dataset_name" md-sort-order="asc" md-card md-fixed-header>

      <!-- Table toolbar has the update button and the search field -->
      <md-table-toolbar>
        <!-- Update button -->
        <div class="md-toolbar-section-start">
            <md-button class="md-dense md-raised button-margin md-primary md-icon-button" @click="fetchDatasets">
              <md-icon>cached</md-icon>
            </md-button>
        </div>
        <!-- Search field -->
        <md-field md-clearable class="md-toolbar-section-end">
          <md-input placeholder="Search by name..." v-model="search" @input="searchOnTable" />
        </md-field>
      </md-table-toolbar>
      <!-- Empty state for table -->
      <md-table-empty-state
        md-label="No datasets found"
        :md-description="`No datasets found for this query. Try a different search term or create a new dataset.`">
      </md-table-empty-state>
      <!-- Definition of how table should look -->
      <md-table-row slot="md-table-row" slot-scope="{ item }">
        <md-table-cell md-label="ID" md-sort-by="id" md-numeric>{{ item.id }}</md-table-cell>
        <md-table-cell md-label="Name" md-sort-by="dataset_name">{{ item.dataset_name }}</md-table-cell>
        <md-table-cell md-label="FilePath" md-sort-by="file_path">{{ item.file_path }}</md-table-cell>
        <md-table-cell md-label="Filetype" md-sort-by="filetype">{{ item.filetype }}</md-table-cell>
        <md-table-cell md-label="HiGlass ID" md-sort-by="higlass_uuid">{{ item.higlass_uuid }}</md-table-cell>
        <md-table-cell md-label="Progress" md-sort-by="completed">
          <!-- item.completed is 1 if completed, 0 if in progress and -1 if failed -->
          <md-icon  v-if="item.completed == 1">done</md-icon>
          <md-progress-spinner :md-diameter="30" md-mode="indeterminate" v-else-if="item.completed == 0"></md-progress-spinner>
          <md-icon v-if="item.completed == -1">error</md-icon>
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
      search: null,
      searched: []
    }),
    methods: {
      searchOnTable () {
        this.searched = searchByName(this.datasets, this.search);
      },
      fetchDatasets() {
        this.fetchData("datasets/")
            .then(response => {
            // success, store datasets
            this.$store.commit("setDatasets", response.data);
            // update datasets
            this.datasets = response.data;
            });
      }
    },
    computed: {
        datasets: {
          get: function() {
            return this.$store.state.datasets; // initial getting from store
          },
          set: function(new_value) {
            this.searched = new_value; // update the sorted list with new values
          }
        }
    },
    created () {
        this.searched = this.datasets;
    }
  }
</script>

<style lang="scss" scoped>
  .md-field {
    max-width: 200px;
  }
</style>