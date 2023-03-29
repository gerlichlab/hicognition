<template>
    <div>
        <md-toolbar class="md-accent" md-elevation="3"
            ><span class="md-title">Processing</span>
            <div style="margin-left: auto">
                <md-button
                    class="md-icon-button"
                    @click="loadProcessingDatasets"
                >
                    <md-icon>cached</md-icon>
                </md-button>
            </div>
        </md-toolbar>

        <md-list v-if="processingDatasets.length != 0">
                <md-list-item v-for="item in processingDatasets" :key="item.id" md-expand>
                    <md-icon class="md-primary">timelapse</md-icon>

                    <div class="md-list-item-text">
                        <span class="md-subheading"
                            ><span class="md-title">Regions </span>{{ item.dataset_name }}</span
                        >
                        <p>Processing...</p>
                    </div>
                    <md-list slot="md-expand">
                        <md-list-item class="md-inset" v-for="processing_feature in item.processing_datasets" :key="`f_${processing_feature}`">
                            <span class="md-subheading"
                                ><span class="md-title">Feature </span
                                >{{ get_name_of_dataset(processing_feature) }}</span
                            >
                        </md-list-item>
                        <md-list-item class="md-inset" v-for="processing_collection in item.processing_collections" :key="`c_${processing_collection}`">
                            <span class="md-subheading"
                                ><span class="md-title">Collection </span
                                >{{ get_name_of_collection(processing_collection) }}</span
                            >
                        </md-list-item>
                    </md-list>
                </md-list-item>
                <md-divider></md-divider>
        </md-list>
        <md-empty-state
            class="md-primary"
            md-icon="done"
            md-label="No processing datasets"
            md-description="Submitted jobs will be displayed here"
            v-else
        >
        </md-empty-state>
    </div>
</template>

<script>
import { mapGetters } from "vuex";
import { apiMixin } from "../../mixins";

export default {
    name: "processingDrawer",
    mixins: [apiMixin],
    components: {
    },
    computed: {
        ...mapGetters(["processingDatasets"])
    },
    methods: {
        loadProcessingDatasets: function() {
            this.fetchAndStoreProcessingDatasets()
        },
        get_name_of_dataset: function(id) {
            return this.$store.getters['getDataset'](id).dataset_name
        },
        get_name_of_collection: function(id) {
            return this.$store.getters['getCollection'](id).name
        }
    },
    mounted: function() {
        // attach event listener to update processing state on notifications
        this.$store.state.notificationSource.addEventListener(
            "notification",
            this.loadProcessingDatasets
        );
    },
    beforeDestroy: function() {
        this.$store.state.notificationSource.removeEventListener(
            "notification",
            this.loadProcessingDatasets
        );
    }
};
</script>
