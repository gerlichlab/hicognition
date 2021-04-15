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
        <div  @mouseleave="hideSelection=true" class="fill-height">
            <div v-if="hideSelection" class="fill-height">
                <div
                    class="md-layout md-gutter md-alignment-center-center fill-height"
                >
                    <md-button @mouseover="hideSelection=false" class="md-icon-button md-primary md-raised"
                        >
                        <md-icon>add</md-icon>
                        </md-button
                    >
                </div>
            </div>
            <div
                class="md-layout md-gutter md-alignment-center-center fill-height"
                v-else
            >
                <md-button @click="setPileup" class="md-raised md-primary"
                    >Pileup</md-button
                >
                <md-button class="md-raised md-primary" @click="setStackup"
                    >Stackup</md-button
                >
                <md-button class="md-raised md-primary" @click="setLineprofile"
                    >Lineprofile</md-button
                >
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
    </div>
</template>

<script>
import pileupWidget from "./widgets/pileupWidget";
import stackupWidget from "./widgets/stackupWidget";
import lineprofileWidget from "./widgets/lineprofileWidget";

export default {
    name: "widgetContainer",
    components: {
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
            selectedType: undefined,
            containerClasses: ["md-elevation-0"],
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
        colIndex: Number
    },
    methods: {
        handleMouseOverSelectionButton: function() {
            this.hideSelection = false;
            setTimeout(() => {this.hideSelection = true}, 1000);
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
        widgetIDExists: function() {
            // checks whether widget id exists
            var queryObject = {
                id: this.id,
                parentID: this.collectionID
            };
            return this.$store.getters["compare/widgetExists"](queryObject);
        },
        initializeWidgetFromEmpty: function() {
            // if state is selected for an empty widget, initializes it for the first time
            var payload = {
                id: this.id,
                rowIndex: this.rowIndex,
                colIndex: this.colIndex,
                parentID: this.collectionID
            };
            // update changed data in store
            this.$store.commit("compare/setWidget", payload);
        },
        setPileup: function() {
            // check if widget is in store
            if (!this.widgetIDExists()) {
                this.initializeWidgetFromEmpty();
            }
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
            // check if widget is in store
            if (!this.widgetIDExists()) {
                this.initializeWidgetFromEmpty();
            }
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
            // check if widget is in store
            if (!this.widgetIDExists()) {
                this.initializeWidgetFromEmpty();
            }
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
        }
    }
};
</script>

<style scoped>
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
