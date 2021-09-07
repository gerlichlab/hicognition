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
                @show-collection-click="
                    showCollectionDialog = true;
                    menuVisible = false;
                "
                @calculate-associations-click="
                    showCalculateAssociations = true;
                    menuVisible = false;
                "
                @embedding-1d-click="
                    showEmbedding1d = true;
                    menuVisible = false;
                "
                @add-assembly-click="
                    showAddAssemblies = true;
                    menuVisible = false;
                "
                @show-assembly-click="
                    showAssemblyDialog = true;
                    menuVisible = false
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
            <collections-dialog
                :dialog="showCollectionDialog"
                @close-dialog="showCollectionDialog = false"
            />
            <preprocess-collections-dialog
                :dialog="showCalculateAssociations"
                @close-dialog="showCalculateAssociations = false"
                datatype="regions"
            />
            <preprocess-collections-dialog
                :dialog="showEmbedding1d"
                @close-dialog="showEmbedding1d = false"
                datatype="1d-features"
            />
            <addAssemblyDialog
                :dialog="showAddAssemblies"
                @close-dialog="showAddAssemblies = false"
            />
            <assemblyDialog
                :dialog="showAssemblyDialog"
                @close-dialog="showAssemblyDialog = false"
            />
            <modify-dataset-dialog
                :dialog="showModifyDialog"
                :datasetID="modifyId"
                @close-dialog="showModifyDialog = false; showMyDatasetDialog = true;"
            />
            <select-dataset-dialog
                :dialog="showSelectDialog"
                :datasets="selectDatasets"
                :datasetType="selectDatasetType"
                @close-dialog="showSelectDialog = false;"
            />
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
import collectionsDialog from "../components/dialogs/collectionsDialog.vue"
import preprocessCollectionsDialog from "../components/dialogs/preprocessCollections.vue"
import addAssemblyDialog from "../components/dialogs/addAssemblyDialog.vue"
import assemblyDialog from "../components/dialogs/assemblyDialog.vue"
import modifyDatasetDialog from "../components/dialogs/modifyDatasetDialog.vue"
import selectDatasetDialog from "../components/dialogs/selectDatasetDialog.vue"

import EventBus from "../eventBus"

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
        addCollectionDialog,
        collectionsDialog,
        preprocessCollectionsDialog,
        addAssemblyDialog,
        assemblyDialog,
        modifyDatasetDialog,
        selectDatasetDialog
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
        showAddCollectionDialog: false,
        showCollectionDialog: false,
        showCalculateAssociations: false,
        showEmbedding1d: false,
        showAddAssemblies: false,
        showAssemblyDialog: false,
        showModifyDialog: false,
        modifyId: undefined,
        selectDatasets: undefined,
        showSelectDialog: false,
        selectDatasetType: undefined
    }),
    mounted: function(){
        // modification listener
        EventBus.$on("show-modify-dialog", (id) => {
            this.modifyId = id
            this.showModifyDialog = true;
            this.showMyDatasetDialog = false;
        })
        // selection listener
        EventBus.$on("show-select-dialog", (datasets, datasetType) => {
            this.selectDatasets = datasets
            this.selectDatasetType = datasetType
            this.showSelectDialog = true
        })

    }
};
</script>
