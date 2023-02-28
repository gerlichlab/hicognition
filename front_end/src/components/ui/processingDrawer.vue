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
            <div v-for="item in processingDatasets" :key="item.id">
                <md-list-item>
                    <md-icon class="md-primary">timelapse</md-icon>

                    <div class="md-list-item-text">
                        <span class="md-subheading"
                            ><span class="md-title">Dataset </span>{{ item.dataset_name }}</span
                        >
                        <p>Processing...</p>
                    </div>
                </md-list-item>
                <md-divider></md-divider>
            </div>
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
