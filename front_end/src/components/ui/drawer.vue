<template>
    <div>
        <md-toolbar class="md-accent" md-elevation="3"
            ><span class="md-title">Data management</span></md-toolbar
        >

        <md-list :md-expand-single="true">
            <md-list-item md-expand>
                <md-icon>multiple_stop</md-icon>
                <span class="md-list-item-text">
                    Regions
                    </span>
                <md-list slot="md-expand">
                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('add-region-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>add</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text"
                            >Add Genomic Regions</span
                        >
                    </md-list-item>

                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('add-metadata-click')"
                        >
                            <md-icon>highlight_alt</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>highlight_alt</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text">Add Metadata</span>
                    </md-list-item>

                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('preprocess-dataset-click')"
                        >
                            <md-icon>launch</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>launch</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text"
                            >Preprocess Features</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('preprocess-collections-click')"
                        >
                            <md-icon>launch</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>launch</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text"
                            >Preprocess Collections</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('mydataset-click', 'bedfile')"
                        >
                            <md-icon>list</md-icon>
                        </md-button>
                        <span class="md-list-item-text">Show Regions</span>
                    </md-list-item>
                </md-list>
            </md-list-item>

            <md-list-item md-expand>
                <md-icon>insights</md-icon>
                <span class="md-list-item-text">Features</span>
                <md-list slot="md-expand">
                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('add-feature-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>add</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text"
                            >Add Genomic Features</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('mydataset-click', 'features')"
                        >
                            <md-icon>list</md-icon>
                        </md-button>
                        <span class="md-list-item-text">Show Features</span>
                    </md-list-item>
                </md-list>
            </md-list-item>

            <md-list-item md-expand>
                <md-icon>layers</md-icon>
                <span class="md-list-item-text">Collections</span>
                <md-list slot="md-expand">
                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('add-collection-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>add</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text"
                            >Create Dataset Collection</span
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
            <md-list-item md-expand>
                <md-icon>circle</md-icon>
                <span class="md-list-item-text">Genomes</span>
                <md-list slot="md-expand">
                    <md-list-item class="md-inset">
                        <md-button
                            v-if=(!isDemo)
                            class="md-icon-button"
                            @click="$emit('add-assembly-click')"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                        <md-button
                            v-if=(isDemo)
                            class="md-icon-button"
                        >
                            <md-icon>add</md-icon>
                            <md-tooltip md-direction="top">Deactivated in demo mode</md-tooltip>
                        </md-button>
                        <span class="md-list-item-text"
                            >Add Genome Assembly</span
                        >
                    </md-list-item>
                    <md-list-item class="md-inset">
                        <md-button
                            class="md-icon-button"
                            @click="$emit('show-assembly-click')"
                        >
                            <md-icon>list</md-icon>
                        </md-button>
                        <span class="md-list-item-text">Show Genomes</span>
                    </md-list-item>
                </md-list>
            </md-list-item>
        </md-list>
    </div>
</template>

<script>
export default {
    name: "drawer",
    data: function() {
        return {
            isDemo: process.env.SHOWCASE
        };
    },
};
</script>
