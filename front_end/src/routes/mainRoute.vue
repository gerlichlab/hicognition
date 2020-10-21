<template>
  <md-app md-waterfall md-mode="fixed-last">
    <md-app-toolbar class="md-large md-dense md-primary">
      <toolbar @drawer-clicked="menuVisible = !menuVisible"></toolbar>
    </md-app-toolbar>

    <md-app-drawer :md-active.sync="menuVisible">
      <drawer
        @mydataset-click="
          showMyDatasetDialog = true;
          menuVisible = false;
        "
        @add-dataset-click="
          showAddDatasetDialog = true;
          menuVisible = false;
        "
      ></drawer>
    </md-app-drawer>

    <md-app-content>
      <router-view></router-view>
      <addDatasetDialog
        :dialog="showAddDatasetDialog"
        @close-dialog="showAddDatasetDialog = false"
      ></addDatasetDialog>
      <datasetDialog
        :dialog="showMyDatasetDialog"
        @close-dialog="showMyDatasetDialog = false"
      ></datasetDialog>
    </md-app-content>
  </md-app>
</template>>

<script>
import toolbar from "../components/toolbar";
import drawer from "../components/drawer";
import datasetDialog from "../components/myDatasetDialog";
import addDatasetDialog from "../components/addDatasetDialog";

export default {
  name: "mainRoute",
  components: {
    toolbar,
    drawer,
    datasetDialog,
    addDatasetDialog,
  },
  data: () => ({
    menuVisible: false,
    showMyDatasetDialog: false,
    showAddDatasetDialog: false,
  })
};
</script>