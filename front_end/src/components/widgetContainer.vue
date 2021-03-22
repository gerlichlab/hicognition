<template>
    <div>
        <div v-if="!isEmpty">
            <div v-if="noWidgetType" :style="cssStyle" class="md-elevation-1 bg">
                <div class="md-layout md-gutter md-alignment-bottom-center fill-half-height">
                    <div class="md-layout-item md-size-90 align-text-center">
                        <span class="md-display-1">Select a widget type</span>
                    </div>
                </div>
                <div class="md-layout md-gutter md-alignment-top-center fill-half-height">
                    <md-button @click="setHiC" class="md-raised md-accent">Hi-C</md-button>
                    <md-button class="md-raised md-accent" @click="setBigWig">BigWig</md-button>
                </div>
            </div>
            <bigwigWidget v-if="this.widgetType == 'BigWig'"
                :height="height"
                :width="width"
                :empty="empty"
                :id="id"
                :collectionID="collectionID"
                :rowIndex="rowIndex"
                :colIndex="colIndex" />
            <hicWidget v-else-if="this.widgetType == 'Hi-C'"
                :height="height"
                :width="width"
                :empty="empty"
                :id="id"
                :collectionID="collectionID"
                :rowIndex="rowIndex"
                :colIndex="colIndex" />
        </div>
        <emptyWidget v-else
            :height="height"
            :width="width"
            :empty="empty"
            :id="collectionID"
            :collectionID="id"
            :rowIndex="rowIndex"
            :colIndex="colIndex"
            @widgetDrop="propagateDrop"/>
    </div>
</template>

<script>
import emptyWidget from "./widgets/emptyWidget"
import hicWidget from "./widgets/hicWidget"
import bigwigWidget from "./widgets/bigwigWidget"

export default {
    name: 'widgetContainer',
    components: {
        emptyWidget,
        bigwigWidget,
        hicWidget
    },
    data: function () {
        // get widget type from store
        var widgetType;
        if (!this.empty){
            var queryObject = {
                    parentID: this.collectionID,
                    id: this.id
                };
            widgetType = this.$store.getters["compare/getWidgetType"](queryObject);
        }else{
            widgetType = undefined;
        }
        return {
            widgetType: widgetType,
            selectedType: undefined,
            widgetTypes: ["Hi-C", "BigWig"]
        }
    },
    props: {
        width: Number,
        height: Number,
        empty: Boolean,
        id: Number,
        collectionID: Number,
        rowIndex: Number,
        colIndex: Number,
    },
    methods: {
        setHiC: function(){
            // set widgetType in store
            var mutationObject = {
                    parentID: this.collectionID,
                    id: this.id,
                    widgetType: "Hi-C"
                };
            this.$store.commit("compare/setWidgetType", mutationObject);
            // set widget Type in this container
            this.widgetType = "Hi-C";
            // TODO rename to something more concrete PileUp Widget?
        },
        setBigWig: function() {
            // set widgetType in store
            var mutationObject = {
                    parentID: this.collectionID,
                    id: this.id,
                    widgetType: "BigWig"
                };
            this.$store.commit("compare/setWidgetType", mutationObject);
            // set widget Type in this container
            this.widgetType = "BigWig";
            // TODO rename to something more concrete Stackup Widget?
            //console.log("Not implemented!");
        },
        propagateDrop: function() {
            // propagates widgetDrop up to widgetCollection
            // Vue events are not automatically passed on to parents https://stackoverflow.com/questions/43559561/how-to-propagate-a-vue-js-event-up-the-components-chain
           this.$emit("widgetDrop", ...arguments);
        }
    },
    computed:{
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            }
        },
        noWidgetType: function() {
            if(this.widgetType){
                return false
            }
            return true
        },
        isEmpty: function() {
            if (this.empty == true){
                return true;
            }else{
                return false;
            }
        }
    }
}
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