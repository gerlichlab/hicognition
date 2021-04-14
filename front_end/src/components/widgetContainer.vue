<template>
    <div>
        <div v-if="!isEmpty">
            <div
                v-if="noWidgetType"
                :style="cssStyle"
                class="md-elevation-1 bg"
            >
                <div
                    class="md-layout md-gutter md-alignment-bottom-center fill-upper-height"
                >
                    <div
                        class="md-layout-item align-text-center"
                    >
                        <span class="md-display-1">Select a widget type</span>
                    </div>
                    <md-speed-dial md-direction="bottom" class="center">
                        <md-speed-dial-target>
                            <md-icon>add</md-icon>
                        </md-speed-dial-target>

                        <md-speed-dial-content>
                            <md-button
                                @click="setPileup"
                                class="md-raised md-accent"
                                >Pileup</md-button
                            >
                            <md-button
                                class="md-raised md-accent"
                                @click="setStackup"
                                >Stackup</md-button
                            >
                            <md-button
                                class="md-raised md-accent"
                                @click="setLineprofile"
                                >Lineplot</md-button
                            >
                        </md-speed-dial-content>
                    </md-speed-dial>
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
        </div>
        <emptyWidget
            v-else
            :height="height"
            :width="width"
            :empty="empty"
            :id="collectionID"
            :collectionID="id"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
            @widgetDrop="propagateDrop"
        />
    </div>
</template>

<script>
import emptyWidget from "./widgets/emptyWidget";
import pileupWidget from "./widgets/pileupWidget";
import stackupWidget from "./widgets/stackupWidget";
import lineprofileWidget from "./widgets/lineprofileWidget";

export default {
    name: "widgetContainer",
    components: {
        emptyWidget,
        stackupWidget,
        pileupWidget,
        lineprofileWidget
    },
    data: function() {
        // get widget type from store
        var widgetType;
        if (!this.empty) {
            var queryObject = {
                parentID: this.collectionID,
                id: this.id
            };
            widgetType = this.$store.getters["compare/getWidgetType"](
                queryObject
            );
        } else {
            widgetType = undefined;
        }
        return {
            widgetType: widgetType,
            selectedType: undefined
        };
    },
    props: {
        width: Number,
        height: Number,
        empty: Boolean,
        id: Number,
        collectionID: Number,
        rowIndex: Number,
        colIndex: Number
    },
    methods: {
        setPileup: function() {
            // set widgetType in store
            var mutationObject = {
                parentID: this.collectionID,
                id: this.id,
                widgetType: "Pileup"
            };
            this.$store.commit("compare/setWidgetType", mutationObject);
            // set widget Type in this container
            this.widgetType = "Pileup";
        },
        setStackup: function() {
            // set widgetType in store
            var mutationObject = {
                parentID: this.collectionID,
                id: this.id,
                widgetType: "Stackup"
            };
            this.$store.commit("compare/setWidgetType", mutationObject);
            // set widget Type in this container
            this.widgetType = "Stackup";
        },
        setLineprofile: function() {
            // set widgetType in store
            var mutationObject = {
                parentID: this.collectionID,
                id: this.id,
                widgetType: "Lineprofile"
            };
            this.$store.commit("compare/setWidgetType", mutationObject);
            // set widget Type in this container
            this.widgetType = "Lineprofile";
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
        },
        isEmpty: function() {
            if (this.empty == true) {
                return true;
            } else {
                return false;
            }
        }
    }
};
</script>

<style scoped>
.bg {
    background-color: rgba(211, 211, 211, 0.2);
}

.align-text-center {
    text-align: center;
}

.fill-width {
    width: 100%;
}

.fill-quarter-height {
    height: 25%;
}

.fill-upper-height {
    height: 35%;
}


.fill-height {
    height: 100%;
}

.md-speed-dial-content {
    height: 200px;
}

.center {
    justify-content: center;
    align-items: center;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -12%);
}

.md-speed-dialt {
    height: auto;
}
</style>
