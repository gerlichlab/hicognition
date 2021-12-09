<template>
    <div class="intermediate-margin">
            <!--assembly and region type--->
            <div class="md-layout md-gutter md-alignment-center-center">
                <div class="md-layout-item md-size-5 small-vertical-margin">
                    <md-button
                        class="
                            md-dense md-raised
                            button-margin
                            md-primary md-icon-button
                        "
                        @click="$emit('load-datasets')"
                    >
                        <md-icon>cached</md-icon>
                    </md-button>
                </div>
                <div class="md-layout-item md-size-25 small-vertical-margin">
                    <md-field class="small-vertical-margin">
                        <label for="assembly">Genome assembly</label>
                        <md-select
                            name="assembly"
                            id="assembly"
                            v-model="selectedAssembly"
                            :disabled="!allowAssemblySelection"
                        >
                            <md-optgroup
                                v-for="(values, org) in assemblies"
                                :key="org"
                                :label="org"
                            >
                                <md-option
                                    v-for="assembly in values"
                                    :key="assembly.id"
                                    :value="assembly.id"
                                    >{{ assembly.name }}</md-option
                                >
                            </md-optgroup>
                        </md-select>
                    </md-field>
                </div>
                <div
                    class="
                        md-layout-item md-layout md-gutter md-size-45
                        small-vertical-margin
                        md-alignment-center-center
                    "
                >
                    <div class="md-layout-item md-size-80">
                        <md-radio
                            v-model="datasetType"
                            value="regions"
                            :disabled="!allowDatasetTypeSelection"
                            >Regions</md-radio
                        >
                        <md-radio
                            v-model="datasetType"
                            value="1d-features"
                            :disabled="!allowDatasetTypeSelection"
                            >1D-features</md-radio
                        >
                    </div>
                </div>
                <div class="md-layout-item md-layout md-gutter md-size-25">
                    <div class="md-layout-item md-size-80 no-padding-right">
                        <md-field>
                            <label>Search</label>
                            <md-input v-model="searchTerm"></md-input>
                        </md-field>
                    </div>
                    <div class="md-layout-item md-size-20 small-padding">
                        <md-button
                            :class="caseButtonClass"
                            @click="matchCase = !matchCase"
                        >
                            <md-icon>text_fields</md-icon>
                            <md-tooltip md-direction="top"
                                >Match Case</md-tooltip
                            >
                        </md-button>
                    </div>
                </div>
            </div>
            <!-- Fields --->
            <div
                class="
                    md-layout md-gutter md-alignment-center-left
                    selection-field
                    md-elevation-2
                    small-vertical-margin
                "
                style="max-height: 50px; overflow: visible"
            >
                <div class="md-layout-item md-size-10 small-vertical-margin">
                    <md-button
                        class="md-icon-button md-accent"
                        @click="
                            showFields = !showFields;
                        "
                    >
                        <md-icon>tune</md-icon>
                    </md-button>
                </div>
                <div class="md-layout-item">
                    <span class="md-caption md-accent">Fields</span>
                </div>
                <div
                    class="
                        md-layout-item md-layout md-gutter md-size-100
                        small-vertical-margin
                        selection-field
                    "
                    v-if="showFields"
                    style="z-index: 500; max-height: 30vh; overflow: auto"
                >
                    <div
                        class="md-layout-item md-size-15"
                        style="padding: 0px"
                        v-for="(value, key) in possibleFields"
                        :key="key"
                    >
                        <md-checkbox v-model="selectedFields" :value="key">{{
                            value
                        }}</md-checkbox>
                    </div>
                </div>
            </div>



            <!--Table--->
            <transition name="fade" mode="out-in">
                <md-table
                    style="max-height: 40vh"
                    v-if="selected.length != 0 && selectedFields.length != 0"
                >
                    <md-table-row
                        style="
                            position: sticky;
                            top: 0;
                            background: white;
                            z-index: 100;
                        "
                    >
                        <md-table-head
                            v-for="(value, key) in fields"
                            :key="key"
                            class="button-container"
                        >
                            <md-button
                                :class="getSortOrderClass(getSortOrderKey(key))"
                                @click="sortByValue(getSortOrderKey(key))"
                            >
                                <md-icon>{{
                                    getSortOrderIcon(getSortOrderKey(key))
                                }}</md-icon>
                            </md-button>
                            <md-button
                                @click="sortByValue(getSortOrderKey(key))"
                            >
                                <span class="md-caption">{{
                                    value
                                }}</span></md-button
                            >
                        </md-table-head>
                    </md-table-row>
                    <md-table-row
                        v-for="collection in selected"
                        :key="collection.id"
                        @click="handleTableRowClicked(collection.id)"
                        :class="getTableRowClass(collection.id)"
                    >
                        <md-table-cell
                            v-for="(value, key) of fields"
                            :key="`${collection.id}-${key}`"
                        >
                            <span
                                v-if="
                                    !['status', 'dataset_ids'].includes(
                                        key
                                    )
                                "
                                >{{ collection[key] }}</span
                            >
                            <span
                            v-if="key === 'dataset_ids'"
                            >
                            <md-button
                                    class="md-secondary"
                                    @click.prevent.stop="
                                        showContainingDatasetsTable(
                                            collection
                                        )
                                    "
                                    :disabled="blockContainedDialog"
                                    >{{ collection.dataset_ids.length }}</md-button
                                >
                            </span>
                            <div v-else-if="key == 'status'">
                                <md-icon
                                    v-if="finishedCollections.includes(collection.id)"
                                    >done</md-icon
                                >
                                <md-progress-spinner
                                    :md-diameter="30"
                                    md-mode="indeterminate"
                                    v-else-if="
                                        processingCollections.includes(collection.id)
                                    "
                                ></md-progress-spinner>
                                <md-icon
                                    v-else-if="
                                        failedCollections.includes(collection.id)
                                    "
                                    >error</md-icon
                                >
                                <md-icon v-else>cloud_done</md-icon>
                            </div>
                        </md-table-cell>
                    </md-table-row>
                </md-table>
                <div
                    v-else-if="
                        (collections.length == 0 || assemblies === undefined) &&
                            !this.showEmpty
                    "
                    class="wait-spinner-container"
                >
                    <div>
                        <md-progress-spinner
                            :md-diameter="100"
                            :md-stroke="10"
                            md-mode="indeterminate"
                        ></md-progress-spinner>
                    </div>
                </div>
                <md-empty-state
                    v-else
                    md-label="No collections found"
                    style="flexgrow: true"
                    :md-description="
                        `No collections found for this query. Try a different search term or create a new dataset.`
                    "
                >
                </md-empty-state>
            </transition>
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";
import EventBus from "../../eventBus";

export default {
    name: "collectionTable",
    mixins: [apiMixin],
    props: {
        collections: Array,
        restrictedDatasetType: String,
        finishedCollections: {
            type: Array,
            default: undefined
        },
        singleSelection: {
            type: Boolean,
            default: true
        },
        showEmpty: {
            type: Boolean,
            default: false
        },
        preselection: {
            type: Array,
            default: () => []
        },
        assembly: {
            type: Number,
            default: undefined
        },
        processingCollections: {
            type: Array,
            default: undefined
        },
        failedCollections: {
            type: Array,
            default: undefined
        },
        blockContainedDialog: {
            type: Boolean,
            default: false
        }
    },
    data: function(){
        let possibleFields;
        if (this.finishedCollections){
            possibleFields = {
                name: "Name",
                "dataset_ids": "Contained datasets",
                status: "Status"
            }
        }else{
            possibleFields = {
                name: "Name",
                "dataset_ids": "Contained datasets",
            }
        }
        return {
            assemblies: undefined,
            selectedFields: Object.keys(possibleFields),
            possibleFields: possibleFields,
            sortBy: undefined,
            sortOrder: "ascending",
            showFields: false,
            searchTerm: "",
            matchCase: false,
            selectedAssembly: undefined,
            selectedIds: [],
            datasetType: "regions",
            allowAssemblySelection: true,
            blockAssemblyBlanking: true
        }
    },
    computed: {
        allowDatasetTypeSelection: function() {
            if (this.restrictedDatasetType) {
                return false;
            }
            return true;
        },
        isSelectionDisabled: function(item) {
            if (this.anyProcessing) {
                return true;
            }
            // check if dataset is owned
            var user_id = this.$store.getters.getUserId;
            if (user_id == item.user_id) {
                return false;
            }
            return true;
        },
        fields: function() {
            const outputFields = {};
            for (let [key, value] of Object.entries(this.possibleFields)) {
                if (this.selectedFields.includes(key)) {
                    outputFields[key] = value;
                }
            }
            return outputFields;
        },
        containedDatasetStyle: function(){
            if (this.selected){
                return {
                    "color": "black"
                }
            }
            return
        },
        caseButtonClass: function() {
            if (this.matchCase) {
                return "md-icon-button md-accent md-raised large-top-margin";
            } else {
                return "md-icon-button large-top-margin";
            }
        },
        selected: function(){
            if (this.collections){
                let fieldFiltered = this.filterCollectionsOnFields(this.collections)
                return this.sortDatasets(this.filterCollectionsOnSearchTerm(fieldFiltered))
            }
        }
    },
    methods: {
        showContainingDatasetsTable(collection) {
            let datasets = this.$store.state.datasets.filter(el => collection.dataset_ids.includes(el.id))
            let datasetType;
            switch (collection.kind){
                case "regions":
                    datasetType = "bedfile"
                    break
                case "1d-features":
                    datasetType = "bigwig"
                    break
                default:
                    datasetType = "cooler"
            }
            EventBus.$emit(
                    "show-select-dialog",
                    datasets,
                    datasetType,
                    [],
                    false,
                    this.selectedAssembly,
                    undefined,
                    undefined,
                    undefined,
                    false
            );
        },
        sortByValue: function(fieldName) {
            if (this.sortBy == fieldName && this.sortOrder == "ascending") {
                this.sortOrder = "descending";
            } else {
                this.sortOrder = "ascending";
            }
            this.sortBy = fieldName;
        },
        filterCollectionsOnSearchTerm(collections) {
            if (this.searchTerm === "") {
                return collections;
            }
            return collections.filter(el => {
                var included = false;
                for (let key of Object.keys(this.fields)) {
                    if (typeof el[key] == "string") {
                        if (this.matchCase) {
                            if (el[key].includes(this.searchTerm)) {
                                included = true;
                            }
                        } else {
                            if (
                                el[key]
                                    .toLowerCase()
                                    .includes(this.searchTerm.toLowerCase())
                            ) {
                                included = true;
                            }
                        }
                    }
                }
                return included;
            });
        },
        filterCollectionsOnFields(collections) {
            return collections.filter(el => {
                return (
                    el.kind == this.datasetType &&
                    el.assembly == this.selectedAssembly
                );
            });
        },
        showDatasetTable: function(datsets){
            console.log("IE")
        },
        getTableRowClass: function(id) {
            if (this.selectedIds.includes(id)) {
                return "blue-background";
            }
            return "";
        },
        handleTableRowClicked: function(id) {
            if (this.singleSelection) {
                if (this.selectedIds.includes(id)){
                    this.selectedIds = []
                }else{
                    this.selectedIds = [id];
                }
            } else if (this.selectedIds.includes(id)) {
                this.selectedIds.splice(this.selectedIds.indexOf(id), 1);
            } else {
                this.selectedIds.push(id);
            }
            this.$emit("selection-changed", this.selectedIds);
        },
        getSortOrderKey(fieldName) {
            if (fieldName == "status") {
                return "processing_state";
            }
            return fieldName;
        },
        getSortOrderClass(fieldName) {
            if (fieldName == this.sortBy) {
                return "md-icon-button md-accent";
            } else {
                return "md-icon-button";
            }
        },
        getSortOrderIcon(fieldName) {
            if (fieldName != this.sortBy) {
                return "sort";
            }
            if (this.sortOrder == "ascending") {
                return "arrow_downward";
            }
            return "arrow_upward";
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then(response => {
                if (response) {
                    this.assemblies = response.data;
                    if (this.assembly) {
                        this.selectedAssembly = this.assembly;
                        this.allowAssemblySelection = false;
                    } else {
                        // set default
                        this.selectedAssembly = this.assemblies["Human"][0].id;
                    }
                }
            });
        },
        sortAscending(datasets) {
            return datasets.sort((a, b) => {
                if (
                    a[this.sortBy] == undefined ||
                    b[this.sortBy] == undefined
                ) {
                    return 1;
                }
                if (Array.isArray(a[this.sortBy])) {
                    return a[this.sortBy].length - b[this.sortBy].length;
                }
                if (
                    a[this.sortBy].toLowerCase() < b[this.sortBy].toLowerCase()
                ) {
                    return -1;
                }
                return 1;
            });
        },
        sortDescending(datasets) {
            return datasets.sort((a, b) => {
                if (
                    a[this.sortBy] == undefined ||
                    b[this.sortBy] == undefined
                ) {
                    return -1;
                }
                if (Array.isArray(a[this.sortBy])) {
                    return b[this.sortBy].length - a[this.sortBy].length;
                }
                if (
                    a[this.sortBy].toLowerCase() > b[this.sortBy].toLowerCase()
                ) {
                    return -1;
                }
                return 1;
            });
        },
        sortDatasets(datasets) {
            if (!this.sortBy) {
                return datasets;
            }
            if (this.sortOrder == "ascending") {
                return this.sortAscending(datasets);
            }
            return this.sortDescending(datasets);
        },
        deleteClicked: function() {
            this.clickedDelete = true;
        },
        handleDelete: async function() {
            return;
        },
        onSelect(item) {
            this.selected = item;
        }
    },
    watch: {
        datasetType: function(){
            this.searchTerm = "";
            this.selectedIds = this.preselection;
            this.$emit("selection-changed", this.selectedIds);
        },
        searchTerm: function() {
            this.selectedIds = this.preselection;
            this.$emit("selection-changed", this.selectedIds);
        },
        selectedAssembly: function() {
            if (this.blockAssemblyBlanking) {
                this.selectedIds = this.preselection;
            } else {
                this.selectedIds = [];
            }
            this.$emit("selection-changed", this.selectedIds);
            this.blockAssemblyBlanking = false;
        },
        collections: function() {
            this.selectedIds = this.preselection;
            this.$emit("selection-changed", this.selectedIds);
        }

    },
    created: function() {
        this.assemblies = this.fetchAssemblies();
        if (this.restrictedDatasetType) {
            this.datasetType = this.restrictedDatasetType;
        }
    }
};
</script>

<style lang="scss" scoped>

.intermediate-margin {
    margin-left: 20px;
    margin-right: 20px;
}

.large-top-margin {
    margin-top: 20px;
}

.small-vertical-margin {
    margin-top: 2px;
    margin-bottom: 5px;
}

.small-padding {
    padding: 5px !important;
}

.no-padding-right {
    padding-right: 0px !important;
}

.selection-field {
    background: rgba(200, 200, 200, 1);
}

.blue-background {
    background: var(--md-theme-default-primary);
}

.top-margin {
    margin-top: 2px;
}

.wait-spinner-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.1s ease;
}
.fade-enter, .fade-leave-to
/* .component-fade-leave-active below version 2.1.8 */ {
    opacity: 0;
}

.md-field {
    max-width: 200px;
}
.md-table {
    max-width: 90vw;
}
.md-table-cell {
    text-align: center;
}

</style>
