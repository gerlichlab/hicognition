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
        <datasetDialog :dialog="showDialog" @close-dialog="showDialog=false"></datasetDialog>
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
}
</script>>