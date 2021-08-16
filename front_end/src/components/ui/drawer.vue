<template>
    <div>
        <md-toolbar class="md-accent" md-elevation="3"
            ><span class="md-title">Data management</span></md-toolbar
        >

        <md-list :md-expand-single="true">
            <md-list-item md-expand>
                <span class="md-list-item-text">Manage Datasets</span>
                <md-list slot="md-expand">
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('add-feature-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Add Genomic Feature</span
                        >
                    </md-list-item>

                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('add-region-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Add Genomic Region</span
                        >
                    </md-list-item>

                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('add-metadata-click')"
                        >
                            <md-icon>highlight_alt</md-icon>
                        </md-button>
                        <span class="md-list-item-text">Add Metadata</span>
                    </md-list-item>

                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('preprocess-dataset-click')"
                        >
                            <md-icon>launch</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Preprocess Datasets</span
                        >
                    </md-list-item>

                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('mydataset-click')"
                        >
                            <md-icon>list</md-icon>
                        </md-button>
                        <span class="md-list-item-text">Show Datasets</span>
                    </md-list-item>
                </md-list>
            </md-list-item>

            <md-list-item md-expand>
                <span class="md-list-item-text">Manage Collections</span>
                <md-list slot="md-expand">
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('add-collection-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Create Dataset Collection</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('calculate-associations-click')"
                        >
                            <md-icon>launch</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Calculate associations</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('embedding-1d-click')"
                        >
                            <md-icon>launch</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Calculate 1D embedding</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('show-collection-click')"
                        >
                            <md-icon>list</md-icon>
                        </md-button>
                        <span class="md-list-item-text"
                            >Show Dataset Collections</span
                        >
                    </md-list-item>
                </md-list>
            </md-list-item>
        </md-list>
    </div>
</template>

<script>
export default {
    name: "drawer",
};
</script>
