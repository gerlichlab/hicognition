<template>
    <div class="intermediate-margin">
        <div
            v-if="datasets === undefined || assemblies === undefined"
            class="wait-spinner-container"
        >
            <md-progress-spinner
                :md-diameter="100"
                :md-stroke="10"
                md-mode="indeterminate"
            ></md-progress-spinner>
        </div>
        <div v-else>
            <!--assembly and region type--->
            <div class="md-layout md-gutter md-alignment-center-center">
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
                <div class="md-layout-item md-size-75 small-vertical-margin">
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
            <!-- Filters --->
            <div class="md-layout md-gutter md-alignment-center-left selection-field md-elevation-2">
                <div class="md-layout-item md-size-10 small-vertical-margin">
                    <md-button class="md-icon-button">
                        <md-icon>filter_alt</md-icon>
                    </md-button>
                </div>
                <div class="md-layout-item">
                    <span class="md-caption">Filter</span>
                </div>
            </div>
            <!-- Fields --->
            <div class="md-layout md-gutter md-alignment-center-left selection-field md-elevation-2 top-margin">
                <div class="md-layout-item md-size-10 small-vertical-margin">
                    <md-button class="md-icon-button">
                        <md-icon>tune</md-icon>
                    </md-button>
                </div>
                <div class="md-layout-item">
                    <span class="md-caption">Fields</span>
                </div>
            </div>
            <!--Table--->
            <transition name="fade" mode="out-in">
                <md-table v-if="selected.length != 0" class="top-margin">
                    <md-table-row>
                        <md-table-head
                            v-for="(value, key) in fields"
                            :key="key"
                            >{{ value }}</md-table-head
                        >
                        <md-table-head>Status</md-table-head>
                    </md-table-row>
                    <md-table-row v-for="dataset in selected" :key="dataset.id">
                        <md-table-cell
                            v-for="(value, key) of fields"
                            :key="`${dataset.id}-${key}`"
                            >{{ dataset[key] }}</md-table-cell
                        >
                        <md-table-cell>
                            <md-icon
                                v-if="dataset.processing_state == 'finished'"
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
                                v-else-if="dataset.processing_state == 'failed'"
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
                        </md-table-cell>
                    </md-table-row>
                </md-table>
                <md-empty-state
                    v-else
                    md-label="No datasets found"
                    :md-description="
                        `No datasets found for this query. Try a different search term or create a new dataset.`
                    "
                >
                </md-empty-state>
            </transition>
        </div>
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";

export default {
    name: "datasetTable",
    mixins: [apiMixin],
    data: () => ({
        datasets: undefined,
        assemblies: undefined,
        selectedAssembly: undefined,
        datasetType: "bedfile"
    }),
    methods: {
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
        fetchDatasets() {
            this.fetchData("datasets/").then(response => {
                if (response) {
                    // success, store datasets
                    this.$store.commit("setDatasets", response.data);
                    // update displayed datasets
                    setTimeout(() => {
                        this.datasets = response.data;
                    }, 100);
                }
            });
        },
        fetchAssemblies() {
            this.fetchData("assemblies/").then(response => {
                if (response) {
                    this.assemblies = response.data;
                    // set default
                    this.selectedAssembly = this.assemblies["Human"][0].id;
                }
            });
        }
    },
    computed: {
        fields: function() {
            return {
                dataset_name: "Name",
                perturbation: "Perturbation",
                cellCycleStage: "Cell cycle Stage"
            };
        },
        selected: function() {
            return this.datasets.filter(el => {
                return (
                    el.filetype == this.datasetType &&
                    el.assembly == this.selectedAssembly
                );
            });
        }
    },
    created: function() {
        this.fetchDatasets();
        this.datasetMetadataMapping = this.$store.getters[
            "getDatasetMetadataMapping"
        ]["DatasetType"];
        this.assemblies = this.fetchAssemblies();
    }
};
</script>

<style lang="scss" scoped>

.intermediate-margin {
    margin-left: 20px;
    margin-right: 20px;
}

.small-vertical-margin {
    margin-top: 2px;
    margin-bottom: 4px;
}

.selection-field {
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
    transition: opacity 0.3s ease;
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
    min-width: 40vw;
}
.md-table-cell {
    text-align: center;
}
</style>
