<template>
    <md-app>
        <md-app-toolbar class="md-dense md-primary">
            <toolbar
                @drawer-clicked="menuVisible = !menuVisible"
                @add-session-click="showAddSessionDialog = true"
                @my-sessions-click="showMySessionsDialog = true"
            ></toolbar>
        </md-app-toolbar>

        <md-app-drawer :md-active.sync="menuVisible">
            <drawer
                @mydataset-click="
                    showMyDatasetDialog = true;
                    menuVisible = false;
                "
                @add-region-click="
                    showAddRegionDialog = true;
                    menuVisible = false;
                "
                @add-feature-click="
                    showAddFeatureDialog = true;
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
                @add-collection-click="
                    showAddCollectionDialog = true;
                    menuVisible = false;
                "
            ></drawer>
        </md-app-drawer>

        <md-app-content>
            <router-view></router-view>
            <addDatasetDialog
                :dialog="showAddRegionDialog"
                @close-dialog="showAddRegionDialog = false"
                datatype="region"
            ></addDatasetDialog>
            <addDatasetDialog
                :dialog="showAddFeatureDialog"
                @close-dialog="showAddFeatureDialog = false"
                datatype="feature"
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
            <mySessionsDialog
                :dialog="showMySessionsDialog"
                @close-dialog="showMySessionsDialog = false"
            ></mySessionsDialog>
            <addCollectionDialog
                :dialog="showAddCollectionDialog"
                @close-dialog="showAddCollectionDialog = false"
            >
            </addCollectionDialog>
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
import addSessionDialog from "../components/dialogs/addSessionDialog";
import mySessionsDialog from "../components/dialogs/mySessionsDialog";
import addCollectionDialog from "../components/dialogs/addCollectionDialog.vue"

export default {
    name: "mainRoute",
    components: {
        toolbar,
        drawer,
        datasetDialog,
        addDatasetDialog,
        addMetadataDialog,
        preprocessDatasetDialog,
        addSessionDialog,
        mySessionsDialog,
        addCollectionDialog
    },
    data: () => ({
        menuVisible: false,
        showMyDatasetDialog: false,
        showAddRegionDialog:false,
        showAddFeatureDialog: false,
        showAddMetadataDialog: false,
        showPreprocessDatasetDialog: false,
        showAddSessionDialog: false,
        showMySessionsDialog: false,
        showAddCollectionDialog: false
    })
};
</script>
