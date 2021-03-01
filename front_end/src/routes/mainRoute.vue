<template>
  <md-app>
    <md-app-toolbar class="md-dense md-primary">
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
        @preprocess-dataset-click="
          showPreprocessDatasetDialog = true;
          menuVisible = false;
        "
        @preprocess-bigwig-click="
          showPreprocessBigwigDialog = true;
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
      <preprocessDatasetDialog
        :dialog="showPreprocessDatasetDialog"
        @close-dialog="showPreprocessDatasetDialog = false"
      ></preprocessDatasetDialog>
      <preprocessBigwigDialog
        :dialog="showPreprocessBigwigDialog"
        @close-dialog="showPreprocessBigwigDialog = false"
      ></preprocessBigwigDialog>
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
import preprocessDatasetDialog from "../components/preProcessDatasetDialog"
import preprocessBigwigDialog from "../components/preProcessBigwigDialog"

export default {
  name: "mainRoute",
  components: {
    toolbar,
    drawer,
    datasetDialog,
    addDatasetDialog,
    preprocessDatasetDialog,
    preprocessBigwigDialog
  },
  data: () => ({
    menuVisible: false,
    showMyDatasetDialog: false,
    showAddDatasetDialog: false,
    showPreprocessDatasetDialog: false,
    showPreprocessBigwigDialog: false
  })
};
</script>