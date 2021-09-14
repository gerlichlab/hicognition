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
                    handleShowMyDatasetDialog
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
                @preprocess-collections-click="
                    showPreprocessCollections = true;
                    menuVisible = false;
                "
                @add-assembly-click="
                    showAddAssemblies = true;
                    menuVisible = false;
                "
                @show-assembly-click="
                    showAssemblyDialog = true;
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
                :datasetType="myDatasetDialogDatasetType"
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
                :dialog="showPreprocessCollections"
                @close-dialog="showPreprocessCollections = false"
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
                @close-dialog="
                    showModifyDialog = false;
                    showMyDatasetDialog = true;
                "
            />
            <select-dataset-dialog
                :dialog="showSelectDialog"
                :datasets="selectDatasets"
                :datasetType="selectDatasetType"
                :singleSelection="singleSelection"
                :preselection="preselection"
                :assembly="selectedAssembly"
                :finishedDatasets="finishedDatasets"
                :processingDatasets="processingDatasets"
                :failedDatasets="failedDatasets"
                :reactToSelection="reactToSelection"
                @close-dialog="showSelectDialog = false"
            />
            <select-collection-dialog
                :dialog="showSelectCollectionDialog"
                :collections="selectCollections"
                :datasetType="selectDatasetTypeCollections"
                :singleSelection="singleSelectionCollections"
                :preselection="preselectionCollections"
                :assembly="selectedAssemblyCollections"
                :finishedCollections="finishedCollections"
                :processingCollections="processingCollections"
                :failedCollections="failedCollections"
                :reactToSelection="reactToSelectionCollections"
                @close-dialog="showSelectCollectionDialog = false"
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
import addCollectionDialog from "../components/dialogs/addCollectionDialog.vue";
import collectionsDialog from "../components/dialogs/collectionsDialog.vue";
import preprocessCollectionsDialog from "../components/dialogs/preprocessCollections.vue";
import addAssemblyDialog from "../components/dialogs/addAssemblyDialog.vue";
import assemblyDialog from "../components/dialogs/assemblyDialog.vue";
import modifyDatasetDialog from "../components/dialogs/modifyDatasetDialog.vue";
import selectDatasetDialog from "../components/dialogs/selectDatasetDialog.vue";
import selectCollectionDialog from "../components/dialogs/selectCollectionDialog.vue"

import EventBus from "../eventBus";

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
        selectDatasetDialog,
        selectCollectionDialog
    },
    data: () => ({
        menuVisible: false,
        showMyDatasetDialog: false,
        myDatasetDialogDatasetType: undefined,
        showAddRegionDialog: false,
        showAddFeatureDialog: false,
        showAddMetadataDialog: false,
        showPreprocessDatasetDialog: false,
        showAddSessionDialog: false,
        showMySessionsDialog: false,
        showAddCollectionDialog: false,
        showCollectionDialog: false,
        showPreprocessCollections: false,
        showAddAssemblies: false,
        showAssemblyDialog: false,
        showModifyDialog: false,
        modifyId: undefined,
        selectDatasets: undefined,
        showSelectDialog: false,
        selectDatasetType: undefined,
        singleSelection: true,
        preselection: [],
        selectedAssembly: undefined,
        finishedDatasets: undefined,
        processingDatasets: undefined,
        failedDatasets: undefined,
        reactToSelection: true,
        showSelectCollectionDialog: false,
        selectCollections: undefined,
        selectDatasetTypeCollections: undefined,
        singleSelectionCollections: undefined,
        preselectionCollections: [],
        selectedAssemblyCollections: undefined,
        finishedCollections: undefined,
        processingCollections: undefined,
        failedCollections: undefined,
        reactToSelectionCollections: undefined
    }),
    methods: {
        handleShowMyDatasetDialog: function(datasetType){
                this.showMyDatasetDialog = true;
                this.menuVisible = false;
                this.myDatasetDialogDatasetType = datasetType
        },
        registerDatasetSelectionHandlers: function () {
            // modification listener
            EventBus.$on("show-modify-dialog", this.handleShowModifyDialog)
            // selection listener
            EventBus.$on("show-select-dialog", this.handleShowSelectDialog)
        },
        handleShowModifyDialog: function (id) {
            this.modifyId = id;
            this.showModifyDialog = true;
            this.showMyDatasetDialog = false;
        },
        handleShowSelectDialog: function (
            datasets,
            datasetType,
            preselection,
            singleSelection = true,
            assembly,
            finishedDatasets,
            processingDatasets,
            failedDatasets,
            reactToSelection = true
        ) {
            this.singleSelection = singleSelection;
            this.selectedAssembly = assembly;
            this.finishedDatasets = finishedDatasets;
            this.processingDatasets = processingDatasets;
            this.failedDatasets = failedDatasets;
            this.reactToSelection = reactToSelection;
            this.preselection = preselection;
            this.selectDatasets = datasets;
            this.selectDatasetType = datasetType;
            this.showSelectDialog = true;
        },
        removeDatasetSelectionEventHandlers: function(){
            // modification listener
            EventBus.$off("show-modify-dialog", this.handleShowModifyDialog)
            // selection listener
            EventBus.$off("show-select-dialog", this.handleShowSelectDialog)
        },
        registerCollectionSelectionHandlers: function(){
            // selection listener
            EventBus.$on("show-select-collection-dialog", this.handleShowSelectCollectionDialog)
        },
        removeCollectionSelectionHandlers: function(){
            EventBus.$off("show-select-collection-dialog", this.handleShowSelectCollectionDialog)
        },
        handleShowSelectCollectionDialog: function (
            collections,
            datasetType,
            preselection,
            singleSelection = true,
            assembly,
            finishedDatasets,
            processingDatasets,
            failedDatasets,
            reactToSelection = true
        ) {
            this.singleSelectionCollections = singleSelection;
            this.selectedAssemblyCollections = assembly;
            this.finishedCollections = finishedDatasets;
            this.processingCollections = processingDatasets;
            this.failedCollections = failedDatasets;
            this.reactToSelectionCollections = reactToSelection;
            this.preselectionCollections = preselection;
            this.selectCollections = collections;
            this.selectDatasetTypeCollections = datasetType;
            this.showSelectCollectionDialog = true;
        },

    },
    mounted: function () {
        this.registerDatasetSelectionHandlers()
        this.registerCollectionSelectionHandlers()
    },
    beforeDestroy: function(){
        this.removeDatasetSelectionEventHandlers()
        this.removeCollectionSelectionHandlers()
    }
};
</script>
