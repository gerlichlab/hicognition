<template>
    <div>
        <div
            v-if="noWidgetType"
            :style="cssStyle"
            :class="containerClasses"
            @dragenter="handleDragEnter"
            @dragleave="handleDragLeave"
            @dragover.prevent
            @drop="handleDrop"
        >
            <div @mouseleave="hideSelection = true" class="fill-height">
                <!-- add icon -->
                <div v-if="hideSelection" class="fill-height">
                    <div
                        class="md-layout md-gutter md-alignment-center-center fill-height no-margin"
                    >
                        <md-button
                            @mouseover="hideSelection = false"
                            class="md-icon-button md-primary md-raised"
                        >
                            <md-icon>add</md-icon>
                        </md-button>
                    </div>
                </div>
                <!-- present list of diagram options when add is hovered over -->
                <div
                    v-else
                    class="md-layout md-gutter md-alignment-center-center fill-height no-margin"
                >
                    <div class="list">
                        <md-list :md-expand-single="true">
                            <md-list-item md-expand>
                                <span class="md-list-item-text">Summary</span>
                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="setWidget('Pileup')"
                                        :disabled="!selectionOptions.pileup"
                                        >Average 2D</md-list-item
                                    >
                                    <md-list-item
                                        class="md-inset"
                                        @click="setWidget('Lineprofile')"
                                        :disabled="
                                            !selectionOptions.lineprofile
                                        "
                                        >Average 1D</md-list-item
                                    >
                                </md-list>
                            </md-list-item>

                            <md-list-item md-expand>
                                <span class="md-list-item-text"
                                    >Individual</span
                                >
                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="setWidget('Stackup')"
                                        :disabled="
                                            !selectionOptions.lineprofile
                                        "
                                        >Stacked lineprofiles</md-list-item
                                    >
                                    <md-list-item
                                        class="md-inset"
                                        @click="setWidget('Embedding1D')"
                                        :disabled="
                                            !selectionOptions.embedding1d
                                        "
                                        >1D-Embedding</md-list-item
                                    >
                                    <md-list-item
                                        class="md-inset"
                                        @click="setWidget('Embedding2D')"
                                        :disabled="
                                            !selectionOptions.embedding2d
                                        "
                                        >2D-Embedding</md-list-item
                                    >
                                </md-list>
                            </md-list-item>

                            <md-list-item md-expand>
                                <span class="md-list-item-text"
                                    >Association</span
                                >
                                <md-list slot="md-expand">
                                    <md-list-item
                                        class="md-inset"
                                        @click="setWidget('Lola')"
                                        :disabled="!selectionOptions.lola"
                                        >Lola</md-list-item
                                    >
                                </md-list>
                            </md-list-item>
                        </md-list>
                    </div>
                </div>
            </div>
        </div>
        <stackupWidget
            v-if="this.widgetType == 'Stackup'"
            :height="height"
            :width="width"
            :empty="empty"
            :id="id"
            :collectionID="collectionID"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
        />
        <pileupWidget
            v-else-if="this.widgetType == 'Pileup'"
            :height="height"
            :width="width"
            :empty="empty"
            :id="id"
            :collectionID="collectionID"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
        />
        <lineprofileWidget
            v-else-if="this.widgetType == 'Lineprofile'"
            :height="height"
            :width="width"
            :empty="empty"
            :id="id"
            :collectionID="collectionID"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
        />
        <lolaWidget
            v-else-if="this.widgetType == 'Lola'"
            :height="height"
            :width="width"
            :empty="empty"
            :id="id"
            :collectionID="collectionID"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
        />
        <embedding-1d-widget
            v-else-if="this.widgetType == 'Embedding1D'"
            :height="height"
            :width="width"
            :empty="empty"
            :id="id"
            :collectionID="collectionID"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
        />
        <embedding-2d-widget
            v-else-if="this.widgetType == 'Embedding2D'"
            :height="height"
            :width="width"
            :empty="empty"
            :id="id"
            :collectionID="collectionID"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
        />
    </div>
</template>

<script>
import pileupWidget from "./widgets/pileupWidget";
import stackupWidget from "./widgets/stackupWidget";
import lineprofileWidget from "./widgets/lineprofileWidget";
import lolaWidget from "./widgets/lolaWidget.vue";
import embedding1dWidget from "./widgets/embedding1DWidget.vue";
import embedding2dWidget from "./widgets/embedding2DWidget.vue";

export default {
    name: "widgetContainer",
    components: {
        stackupWidget,
        pileupWidget,
        lineprofileWidget,
        lolaWidget,
        embedding1dWidget,
        embedding2dWidget
    },
    data: function() {
        // get widget type from store
        var widgetType;
        if (!this.empty) {
            widgetType = this.$store.getters["compare/getWidgetType"]({
                parentID: this.collectionID,
                id: this.id
            });
        } else {
            widgetType = undefined;
        }
        return {
            widgetType: widgetType,
            selectedType: undefined,
            containerClasses: ["md-elevation-0", "small-margin"],
            hideSelection: true
        };
    },
    props: {
        width: Number,
        height: Number,
        empty: Boolean,
        id: Number,
        collectionID: Number,
        rowIndex: Number,
        colIndex: Number,
        selectionOptions: Object
    },
    methods: {
        handleExpandClick: function(event, key) {
            console.log(event);
            if (!selectionOptions[key]) {
            }
        },
        handleMouseOverSelectionButton: function() {
            this.hideSelection = false;
            setTimeout(() => {
                this.hideSelection = true;
            }, 1000);
        },
        handleDragEnter: function(e) {
            this.containerClasses.push("dark-background");
        },
        handleDragLeave: function(e) {
            this.containerClasses.pop();
        },
        handleDrop: function(event) {
            var sourceWidgetID = event.dataTransfer.getData("widget-id");
            var sourceColletionID = event.dataTransfer.getData("collection-id");
            this.containerClasses.pop();
            this.$emit(
                "widgetDrop",
                Number(sourceColletionID),
                Number(sourceWidgetID),
                this.rowIndex,
                this.colIndex
            );
        },
        setWidget: function(widgetType) {
            // check if widget is in store
            var idExists = this.$store.getters["compare/widgetExists"]({
                id: this.id,
                parentID: this.collectionID
            });
            if (!idExists) {
                // initialize widget
                this.$store.commit("compare/setWidget", {
                    id: this.id,
                    rowIndex: this.rowIndex,
                    colIndex: this.colIndex,
                    parentID: this.collectionID
                });
            }
            // set widget Type in this container
            this.widgetType = widgetType;
            // set it in store
            this.$store.commit(
                "compare/setWidgetType",
                {
                    parentID: this.collectionID,
                    id: this.id,
                    widgetType: widgetType
                }
            );
        },
        propagateDrop: function() {
            // propagates widgetDrop up to widgetCollection
            // Vue events are not automatically passed on to parents https://stackoverflow.com/questions/43559561/how-to-propagate-a-vue-js-event-up-the-components-chain
            this.$emit("widgetDrop", ...arguments);
        }
    },
    computed: {
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            };
        },
        noWidgetType: function() {
            if (this.widgetType) {
                return false;
            }
            return true;
        }
    }
};
</script>

<style scoped>
.small-margin {
    margin: 2px;
}

.no-margin {
    margin: 0px;
}

.dark-background {
    background-color: grey;
    opacity: 0.5;
}

.align-text-center {
    text-align: center;
}

.fill-half-height {
    height: 50%;
}

.fill-height {
    height: 100%;
}
</style>
