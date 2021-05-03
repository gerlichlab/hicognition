<template>
    <md-app>
        <md-app-toolbar class="md-dense md-primary">
            <toolbar @drawer-clicked="menuVisible = !menuVisible" @add-session-click="showAddSessionDialog = true"></toolbar>
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
                @add-metadata-click="
                    showAddMetadataDialog = true;
                    menuVisible = false;
                "
                @preprocess-dataset-click="
                    showPreprocessDatasetDialog = true;
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
            <addMetadataDialog
                :dialog="showAddMetadataDialog"
                @close-dialog="showAddMetadataDialog = false"
            ></addMetadataDialog>
            <preprocessDatasetDialog
                :dialog="showPreprocessDatasetDialog"
                @close-dialog="showPreprocessDatasetDialog = false"
            ></preprocessDatasetDialog>
            <datasetDialog
                :dialog="showMyDatasetDialog"
                @close-dialog="showMyDatasetDialog = false"
            ></datasetDialog>
            <addSessionDialog
                :dialog="showAddSessionDialog"
                @close-dialog="showAddSessionDialog = false"
            ></addSessionDialog>
        </md-app-content>
    </md-app>
</template>

<script>
import toolbar from "../components/ui/toolbar";
import drawer from "../components/ui/drawer";
import datasetDialog from "../components/dialogs/myDatasetDialog";
import addDatasetDialog from "../components/dialogs/addDatasetDialog";
import addMetadataDialog from "../components/dialogs/addMetadataDialog";
import preprocessDatasetDialog from "../components/dialogs/preProcessDatasetDialog";
import addSessionDialog from "../components/dialogs/addSessionDialog"

export default {
    name: "mainRoute",
    components: {
        toolbar,
        drawer,
        datasetDialog,
        addDatasetDialog,
        addMetadataDialog,
        preprocessDatasetDialog,
        addSessionDialog
    },
    data: () => ({
        menuVisible: false,
        showMyDatasetDialog: false,
        showAddDatasetDialog: false,
        showAddMetadataDialog: false,
        showPreprocessDatasetDialog: false,
        showAddSessionDialog: false
    })
};
</script>
