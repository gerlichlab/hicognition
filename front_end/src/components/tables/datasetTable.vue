<template>
    <div class="intermediate-margin">
        <div>
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
                        <md-radio v-model="datasetType" value="bedfile"
                            >Region</md-radio
                        >
                        <md-radio v-model="datasetType" value="bigwig"
                            >1D-feature</md-radio
                        >
                        <md-radio v-model="datasetType" value="cooler"
                            >2D-feature</md-radio
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
            <!-- Filters --->
            <div
                class="
                    md-layout md-gutter md-alignment-center-left
                    selection-field
                    md-elevation-2
                "
                style="max-height: 50px; overflow: visible"
            >
                <div class="md-layout-item md-size-10 small-vertical-margin">
                    <md-button
                        class="md-icon-button md-accent"
                        @click="
                            showFilters = !showFilters;
                            showFields = false;
                        "
                    >
                        <md-icon>filter_alt</md-icon>
                    </md-button>
                </div>
                <div class="md-layout-item">
                    <span class="md-caption md-accent">Filter</span>
                </div>
                <div
                    class="
                        md-layout-item md-layout md-gutter md-size-100
                        small-vertical-margin
                        selection-field
                        small-padding
                    "
                    v-if="showFilters"
                    style="z-index: 500; max-height: 30vh; overflow: auto"
                >
                    <div class="md-layout-item md-layout md-gutter md-size-100">
                        <div
                            class="md-layout-item md-size-20 small-padding"
                            v-for="(value, key) in filterFields"
                            :key="key"
                        >
                            <md-menu
                                md-direction="bottom-start"
                                md-size="auto"
                                md-align-trigger
                                :mdCloseOnClick="false"
                                :mdCloseOnSelect="false"
                            >
                                <md-button md-menu-trigger class="md-raised">{{
                                    value
                                }}</md-button>

                                <md-menu-content
                                    style="z-index: 500"
                                    class="blue-background"
                                >
                                    <md-menu-item
                                        v-for="option in getFieldOptions(value)"
                                        :key="option"
                                        @click="
                                            setFilterSelection(value, option)
                                        "
                                        :class="getOptionClass(value, option)"
                                        >{{ option }}</md-menu-item
                                    >
                                </md-menu-content>
                            </md-menu>
                        </div>
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
                            showFilters = false;
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
                            <md-button :class="getSortOrderClass(getSortOrderKey(key))" @click="sortByValue(getSortOrderKey(key))">
                                <md-icon>{{ getSortOrderIcon(getSortOrderKey(key)) }}</md-icon>
                            </md-button>
                            <md-button @click="sortByValue(getSortOrderKey(key))">
                                <span class="md-caption">{{
                                    value
                                }}</span></md-button
                            >
                        </md-table-head>
                    </md-table-row>
                    <md-table-row
                        v-for="dataset in selected"
                        :key="dataset.id"
                        @click="handleTableRowClicked(dataset.id)"
                        :class="getTableRowClass(dataset.id)"
                    >
                        <md-table-cell
                            v-for="(value, key) of fields"
                            :key="`${dataset.id}-${key}`"
                        >
                            <span v-if="key != 'status'">{{
                                dataset[key]
                            }}</span>
                            <div v-else>
                                <md-icon
                                    v-if="
                                        dataset.processing_state == 'finished'
                                    "
                                    >done</md-icon
                                >
                                <md-progress-spinner
                                    :md-diameter="30"
                                    md-mode="indeterminate"
                                    v-else-if="
                                        dataset.processing_state == 'processing'
                                    "
                                ></md-progress-spinner>
                                <md-icon
                                    v-else-if="
                                        dataset.processing_state == 'failed'
                                    "
                                    >error</md-icon
                                >
                                <md-icon
                                    v-else-if="
                                        dataset.processing_state == 'uploaded'
                                    "
                                    >cloud_done</md-icon
                                >
                                <md-icon
                                    v-else-if="
                                        dataset.processing_state == 'uploading'
                                    "
                                    >cloud_upload</md-icon
                                >
                            </div>
                        </md-table-cell>
                    </md-table-row>
                </md-table>
                <div
                    v-else-if="datasets.length == 0 || assemblies === undefined"
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
                    md-label="No datasets found"
                    style="flexgrow: true"
                    :md-description="`No datasets found for this query. Try a different search term or create a new dataset.`"
                >
                </md-empty-state>
            </transition>
        </div>
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";

const fieldToPropertyMapping = {
    Method: "method",
    SizeType: "sizeType",
    Normalization: "normalization",
    DerivationType: "derivationType",
    Protein: "protein",
    Directionality: "directionality",
};

export default {
    name: "datasetTable",
    mixins: [apiMixin],
    props: {
        datasets: Array,
    },
    data: () => ({
        assemblies: undefined,
        searchTerm: "",
        matchCase: false,
        selectedAssembly: undefined,
        selectedIds: [],
        datasetMetadataMapping: undefined,
        filterSelection: [],
        filterFields: {},
        sortBy: undefined,
        sortOrder: "ascending",
        selectedFields: [
            "dataset_name",
            "valueType",
            "perturbation",
            "cellCycleStage",
            "status",
        ],
        showFilters: false,
        showFields: false,
        datasetType: "bedfile",
    }),
    methods: {
        getSortOrderKey(fieldName){
            if (fieldName == "status"){
                return "processing_state"
            }
            return fieldName
        },
        getSortOrderClass(fieldName){
            if (fieldName == this.sortBy){
                return "md-icon-button md-accent"
            }else{
                return "md-icon-button"
            }
        },
        getSortOrderIcon(fieldName){
            if (fieldName != this.sortBy){
                return "sort"
            }
            if (this.sortOrder == "ascending"){
                return "arrow_downward"
            }
            return "arrow_upward"
        },
        sortByValue: function (fieldName) {
            if (this.sortBy == fieldName && this.sortOrder == "ascending") {
                this.sortOrder = "descending";
            } else {
                this.sortOrder = "ascending";
            }
            this.sortBy = fieldName;
        },
        getTableRowClass: function (id) {
            if (this.selectedIds.includes(id)) {
                return "blue-background";
            }
            return "";
        },
        handleTableRowClicked: function (id) {
            if (this.selectedIds.includes(id)) {
                this.selectedIds.splice(this.selectedIds.indexOf(id), 1);
            } else {
                this.selectedIds.push(id);
            }
            this.$emit("selection-changed", this.selectedIds);
        },
        getOptionClass: function (field, value) {
            let filterString = `${field}-${value}`;
            if (this.filterSelection.includes(filterString)) {
                return "blue-background";
            }
            return "";
        },
        setFilterSelection: function (field, value) {
            let filterString = `${field}-${value}`;
            if (this.filterSelection.includes(filterString)) {
                this.filterSelection.splice(
                    this.filterSelection.indexOf(filterString),
                    1
                );
            } else {
                this.filterSelection.push(filterString);
            }
        },
        getFieldOptions: function (field) {
            if (field == "ValueType") {
                return Object.keys(
                    this.datasetMetadataMapping[this.datasetType]["ValueType"]
                );
            }
            if (field == "Protein") {
                return undefined;
            }
            let fieldValues = new Set();
            for (let options of Object.values(
                this.datasetMetadataMapping[this.datasetType]["ValueType"]
            )) {
                if (field in options) {
                    options[field].forEach((element) =>
                        fieldValues.add(element)
                    );
                }
            }
            if (fieldValues.size == 0) {
                return undefined;
            }
            return Array.from(fieldValues);
        },
        isSelectionDisabled: function (item) {
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
        fetchAssemblies() {
            this.fetchData("assemblies/").then((response) => {
                if (response) {
                    this.assemblies = response.data;
                    // set default
                    this.selectedAssembly = this.assemblies["Human"][0].id;
                }
            });
        },
        filterDatasetsOnFields(datasets) {
            return datasets.filter((el) => {
                return (
                    el.filetype == this.datasetType &&
                    el.assembly == this.selectedAssembly
                );
            });
        },
        filterDatasetsOnMetadata(datasets) {
            return datasets.filter((el) => {
                let output = true;
                let atLeastOne = false;
                for (let [key, value] of Object.entries(this.filterFields)) {
                    if (!el[key]) {
                        continue;
                    }
                    let filterString = `${value}-${el[key]}`;
                    atLeastOne = true;
                    if (!this.filterSelection.includes(filterString)) {
                        output = false;
                    }
                }
                return output && atLeastOne;
            });
        },
        filterDatasetsOnSearchTerm(datasets) {
            if (this.searchTerm === "") {
                return datasets;
            }
            return datasets.filter((el) => {
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
        sortAscending(datasets) {
            return datasets.sort((a, b) => {
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
        createFilterFields() {
            let fields = {};
            this.filterSelection = [];
            for (let [key, value] of Object.entries(this.possibleFields)) {
                if (this.getFieldOptions(value)) {
                    this.getFieldOptions(value).map((option) => {
                        let filterString = `${value}-${option}`;
                        this.filterSelection.push(filterString);
                    });
                    fields[key] = value;
                }
            }
            this.filterFields = fields;
        },
    },
    computed: {
        caseButtonClass: function () {
            if (this.matchCase) {
                return "md-icon-button md-accent md-raised large-top-margin";
            } else {
                return "md-icon-button large-top-margin";
            }
        },
        showStatus: function () {
            return this.selectedFields.includes("status");
        },
        possibleFields: function () {
            const outputFields = {
                dataset_name: "Name",
                valueType: "ValueType",
                perturbation: "Perturbation",
                cellCycleStage: "Cell cycle Stage",
            };
            let fields = new Set();
            // go through possible fields of this value type
            for (let valueType of Object.keys(
                this.datasetMetadataMapping[this.datasetType]["ValueType"]
            )) {
                Object.keys(
                    this.datasetMetadataMapping[this.datasetType]["ValueType"][
                        valueType
                    ]
                ).forEach((element) => fields.add(element));
            }
            Array.from(fields.values()).forEach(
                (element) =>
                    (outputFields[fieldToPropertyMapping[element]] = element)
            );
            // put in status
            outputFields["status"] = "Status";
            return outputFields;
        },
        fields: function () {
            const outputFields = {};
            for (let [key, value] of Object.entries(this.possibleFields)) {
                if (this.selectedFields.includes(key)) {
                    outputFields[key] = value;
                }
            }
            return outputFields;
        },
        selected: function () {
            if (this.datasets) {
                // if filters run reset selection
                let fieldFiltered = this.filterDatasetsOnFields(this.datasets);
                let metadataFiltered =
                    this.filterDatasetsOnMetadata(fieldFiltered);
                let filteredOnSearchTerm =
                    this.filterDatasetsOnSearchTerm(metadataFiltered);
                return this.sortDatasets(filteredOnSearchTerm);
            }
            return [];
        },
    },
    watch: {
        datasetType: function () {
            this.createFilterFields();
            this.searchTerm = "";
            this.selectedIds = [];
            this.$emit("selection-changed", this.selectedIds);
        },
        searchTerm: function () {
            this.selectedIds = [];
            this.$emit("selection-changed", this.selectedIds);
        },
        filterFields: function () {
            this.selectedIds = [];
            this.$emit("selection-changed", this.selectedIds);
        },
        selectedAssembly: function () {
            this.selectedIds = [];
            this.$emit("selection-changed", this.selectedIds);
        },
        datasets: function () {
            this.selectedIds = [];
            this.$emit("selection-changed", this.selectedIds);
        },
    },
    created: function () {
        this.datasetMetadataMapping =
            this.$store.getters["getDatasetMetadataMapping"]["DatasetType"];
        this.assemblies = this.fetchAssemblies();
        this.createFilterFields();
    },
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
