<template>
  <div>
    <md-table v-model="searched" md-sort="dataset_name" md-sort-order="asc" md-card md-fixed-header>
      <md-table-toolbar>
        <div class="md-toolbar-section-start">
        </div>

        <md-field md-clearable class="md-toolbar-section-end">
          <md-input placeholder="Search by name..." v-model="search" @input="searchOnTable" />
        </md-field>
      </md-table-toolbar>

      <md-table-empty-state
        md-label="No datasets found"
        :md-description="`No datasets found for this '${search}' query. Try a different search term or create a new dataset.`">
        <md-button class="md-primary md-raised" @click="newDataset">Create New User</md-button>
      </md-table-empty-state>

      <md-table-row slot="md-table-row" slot-scope="{ item }">
        <md-table-cell md-label="ID" md-sort-by="id" md-numeric>{{ item.id }}</md-table-cell>
        <md-table-cell md-label="Name" md-sort-by="dataset_name">{{ item.dataset_name }}</md-table-cell>
        <md-table-cell md-label="FilePath" md-sort-by="file_path">{{ item.file_path }}</md-table-cell>
        <md-table-cell md-label="Filetype" md-sort-by="filetype">{{ item.filetype }}</md-table-cell>
        <md-table-cell md-label="HiGlass ID" md-sort-by="higlass_uuid">{{ item.higlass_uuid }}</md-table-cell>
        <md-table-cell md-label="Progress" md-sort-by="completed">
          <md-icon  v-if="item.completed">done</md-icon>
          <md-progress-spinner :md-diameter="30" md-mode="indeterminate" v-else></md-progress-spinner>
        </md-table-cell>
      </md-table-row>
    </md-table>
  </div>
</template>

<script>
  const toLower = text => {
    return text.toString().toLowerCase()
  }

  const searchByName = (items, term) => {
    if (term) {
      var filtered_items = items.filter(item => {
          return toLower(item.dataset_name).includes(toLower(term))
          });
      return filtered_items
    }

    return items
  }

  export default {
    name: 'datasetTable',
    data: () => ({
      search: null,
      searched: []
    }),
    methods: {
      newDataset () {
        window.alert('Noop')
      },
      searchOnTable () {
        this.searched = searchByName(this.datasets, this.search);
      }
    },
    computed: {
        datasets: function() {
          return this.$store.state.datasets
        }
    },
    created () {
        this.searched = this.datasets;
        console.log(this.searched)
    }
  }
</script>

<style lang="scss" scoped>
  .md-field {
    max-width: 300px;
  }
</style>