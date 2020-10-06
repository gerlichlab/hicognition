<template>

  <md-app md-waterfall md-mode="fixed-last">
      <md-app-toolbar class="md-large md-dense md-primary">
        <toolbar @drawer-clicked="menuVisible = !menuVisible"></toolbar>
      </md-app-toolbar>

      <md-app-drawer :md-active.sync="menuVisible">
        <drawer @mydataset-click="showDialog=true; menuVisible=false"></drawer>
      </md-app-drawer>

      <md-app-content>
        <router-view></router-view>
        <datasetDialog :dialog="showDialog" @close-dialog="showDialog=false" @get-datasets="getDatasets"></datasetDialog>
      </md-app-content>
  </md-app>
</template>>

<script>

import toolbar from "../components/toolbar";
import drawer from "../components/drawer";
import datasetDialog from "../components/myDatasetDialog"

export default {
name: "mainRoute",
  components: {
    toolbar,
    drawer,
    datasetDialog
  },
  data: () => ({
    menuVisible: false,
    showDialog: false
  }),
  methods: {
    getDatasets: function () {
        var token = this.$store.state.token;
        var encodedToken = btoa(token + ":")
        this.$http.get(process.env.API_URL + "datasets/", {
          headers: {
            "Authorization": `Basic ${encodedToken}`
          }
        }).then(response => {
          if (response.status != 200){
            console.log(`Error: ${response.data}`);
          }else{
            // success, store datasets
            this.$store.commit("setDatasets", response.data)
          }
        })
    }
  },
  created: function () {
    // get datasets when route is created
    this.getDatasets()
  }
}
</script>>