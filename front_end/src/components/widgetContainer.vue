<template>
    <div>
            <div
                v-if="noWidgetType"
                :style="cssStyle"
                class="md-elevation-1 bg"
            >
                <div
                    class="md-layout md-gutter md-alignment-bottom-center fill-half-height"
                >
                    <div class="md-layout-item md-size-90 align-text-center">
                        <span class="md-display-1">Select a widget type</span>
                    </div>
                </div>
                <div
                    class="md-layout md-gutter md-alignment-top-center fill-half-height"
                >
                    <md-button @click="setPileup" class="md-raised md-accent"
                        >Pileup</md-button
                    >
                    <md-button class="md-raised md-accent" @click="setStackup"
                        >Stackup</md-button
                    >
                    <md-button class="md-raised md-accent" @click="setLineprofile"
                        >Lineprofile</md-button
                    >
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
        widgetIDExists: function(){
            // checks whether widget id exists
            var queryObject = {
                id: this.id,
                parentID: this.collectionID
            }
            return this.$store.getters["compare/pileupExists"](queryObject)
        },
        initializeWidgetFromEmpty: function(){
            // if state is selected for an empty widget, initializes it for the first time
            var payload = {
                id: this.id,
                rowIndex: this.rowIndex,
                colIndex: this.colIndex,
                parentID: this.collectionID
            }
            // update changed data in store
            this.$store.commit("compare/setWidget", payload);
        },
        setPileup: function() {
            // check if widget is in store
            if (!this.widgetIDExists()){
                this.initializeWidgetFromEmpty()
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
            if (!this.widgetIDExists()){
                this.initializeWidgetFromEmpty()
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
            if (!this.widgetIDExists()){
                this.initializeWidgetFromEmpty()
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
.bg {
    background-color: rgba(211, 211, 211, 0.2);
}

.align-text-center {
    text-align: center;
}

.fill-half-height {
    height: 50%;
}
</style>
