<template>
<div @dragenter="expandCollection" @dragleave="handleDragLeave">
    <md-card :style="cssStyle" ref="collectionCard">
        <md-card-header>
            <div class="md-layout">
                <div class="md-layout-item md-size-30 padding-right">
                    <div class="menu-button">
                        <md-button @click="handleZoomIn" class="md-icon-button">
                            <md-icon>zoom_in</md-icon>
                        </md-button>
                    </div>
                    <div class="menu-button">
                        <md-button @click="handleZoomOut" class="md-icon-button" :disabled="blockZoomOut">
                            <md-icon>zoom_out</md-icon>
                        </md-button>
                    </div>
                </div>
                <div class="md-layout-item md-size-30 padding-right">
                    <md-field class="padding-top">
                        <md-select
                        v-model="selectedRegionID"
                        name="region"
                        id="region"
                        placeholder="Region"
                        >
                        <md-option
                            v-for="item in regions"
                            :value="item.id"
                            :key="item.id"
                            >{{ item.dataset_name }}</md-option
                        >
                        </md-select>
                    </md-field>
                </div>
                <div class="md-layout-item md-size-25">
                    <md-field class="padding-top">
                        <md-select
                        v-model="selectedWindowSize"
                        name="region"
                        id="region"
                        placeholder="Size"
                        :disabled="!windowSizesAvailable"
                        >
                        <md-option
                            v-for="item in windowSizes"
                            :value="item.id"
                            :key="item.id"
                            >{{ item.windowsize }}</md-option
                        >
                        </md-select>
                    </md-field>
                </div>
                <div class="md-layout-item md-size-10 padding-left">
                    <div class="menu-button">
                        <md-button @click="fetchDatasets" class="md-icon-button md-dense md-raised button-margin md-primary md-icon-button">
                            <md-icon>cached</md-icon>
                        </md-button>
                    </div>
                </div>
            </div>
        <md-divider></md-divider>
        </md-card-header>
        <md-card-content class="nomargin">
            <widget class="inline"  v-for="item in flattenedElements" :key="item.id"
                                                      :height="item.height"
                                                      :width="item.width"
                                                      :empty="item.empty"
                                                      :id="item.id"
                                                      :collectionID="id"
                                                      :rowIndex="item.rowIndex"
                                                      :colIndex="item.colIndex"
                                                      @widgetDrop="handleWidgetDrop" />
        </md-card-content>
        <md-card-actions>
            <md-button @click="deleteCollection" class="md-primary md-raised">Delete</md-button>
        </md-card-actions>
    </md-card>
</div>
</template>

<script>

import widget from "./widget"
import Widget from './widget.vue'
import { apiMixin } from "../mixins";

export default {
    name: 'widgetCollection',
    mixins: [apiMixin],
    props: {
        id: Number
    },
    components: {
        widget
    },
    data: function () {
        return {
            regions: [],
            windowSizes: [],
            selectedRegionID: null,
            selectedWindowSize: null,
            marginSizeWidth: 4,
            marginSizeHeight: 10,
            paddingWidth: 11,
            paddingHeight: 130,
            baseWidth: 350,
            baseHeight: 350,
            maxRowNumber: 0,
            maxColumnNumber: 0,
            children: []
        }
    },
    computed: {
        windowSizesAvailable: function() {
            if (this.windowSizes.length != 0){
                return true
            }
            return false
        },
        blockZoomOut: function() {
            if (this.baseWidth <= 350){
                return true
            }
            return false
        },
        collectionHeight: function() {
            return (this.maxRowNumber + 1) * this.baseHeight;
        },
        collectionWidth: function() {
            return (this.maxColumnNumber + 1) * this.baseWidth;
        },
        elementMatrix: function(){
            // creates element matrix from children filled up with empty elements
            var matrix = [];
            // create empty matrix
            for (var rowIndex = 0; rowIndex <= this.maxRowNumber; rowIndex++){
                var emptyRow = [];
                for(var colIndex = 0; colIndex <= this.maxColumnNumber; colIndex++){
                    emptyRow[colIndex] = {
                        id: this.getNextID(),
                        height: this.baseHeight,
                        width: this.baseWidth,
                        empty: true,
                        rowIndex: rowIndex,
                        colIndex: colIndex,
                        parentID: this.id,
                    }
                }
                matrix.push(emptyRow);
            }
            // fill in children
            for (var child of this.children){
                matrix[child.rowIndex][child.colIndex] = {
                    id: child.id,
                        height: this.baseHeight,
                        width: this.baseWidth,
                        empty: false,
                        rowIndex: child.rowIndex,
                        colIndex: child.colIndex,
                        text: child.text,
                        parentID: this.id
                }
            }
            return matrix;
        },
        flattenedElements: function() {
            // gives a flattened representation of elements
            var output = [];
            for (var row of this.elementMatrix){
                for (var element of row){
                    output.push(element);
                }
            }
            return output;
        },
        cssStyle: function() {
            return {
                height: `${this.collectionHeight + this.paddingHeight  + (this.maxRowNumber + 1) * this.marginSizeHeight}px`,
                width: `${this.collectionWidth + this.paddingWidth  + (this.maxColumnNumber + 1) * this.marginSizeWidth}px`
            }
        }
    },
    methods: {
        getNextID: function() {
            return Math.floor(Math.random() * 1000000000);
        },
        fetchDatasets: function() {
        this.fetchData("datasets/").then((response) => {
                // success, store datasets
                this.$store.commit("setDatasets", response.data);
                // update datasets; Only use completed datasets
                this.regions = response.data.filter(
                (element) => element.filetype == "bedfile" && (element.processing_state == "finished")
                );
            });
        },
        handleZoomIn: function() {
            this.baseWidth += 50;
            this.baseHeight += 50;
        },
        handleZoomOut: function() {
            this.baseWidth -= 50;
            this.baseHeight -= 50;
        },
        expandCollection: function(){
            // needed for showing region before widgetdrop
            var maxRowElements = Math.max(...this.children.map((element) => element.rowIndex));
            var maxColElements = Math.max(...this.children.map((element) => element.colIndex));
            this.maxRowNumber = maxRowElements + 1;
            this.maxColumnNumber = maxColElements + 1;
        },
        handleDragLeave: function(e){
            // check if card is collection card, all child elements trigger leave events
            if ((e.toElement == this.$refs["collectionCard"].$el) || (e.toElement.contains(this.$refs["collectionCard"].$el))){
                // if dragleave on collection card -> shrink collection
                this.setTightBoundingArea()
            }
        },
        setTightBoundingArea: function(e) {
            // resizes drawn widgetmatrix to to largest element in children
            this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
            this.maxColumnNumber = Math.max(...this.children.map((element) => element.colIndex));
        },
        deleteCollection: function() {
            this.$store.commit("compare/deleteWidgetCollection", this.id);
        },
        handleWidgetDrop: function(sourceColletionID, sourceWidgetID, rowIndex, colIndex) {
            // obtain data from store
            var queryObject = {
                parentID: sourceColletionID,
                id: sourceWidgetID
            };
            var widgetData = this.$store.getters["compare/getWidgetProperties"](queryObject);
            // check if interval needs to be updated. Compares old interval of source widget collection and this collection
            var newIntervalID = this.$store.getters["compare/getCollectionProperties"](this.id)["intervalID"];
            var oldIntervalID = this.$store.getters["compare/getCollectionProperties"](sourceColletionID)["intervalID"];
            // delete original widget in store
            this.$store.commit("compare/deleteWidget", queryObject);
            // update widget data that changed upon drop
            widgetData["id"] = this.getNextID();
            widgetData["rowIndex"] = rowIndex;
            widgetData["colIndex"] = colIndex;
            widgetData["parentID"] = this.id;
            if (newIntervalID != oldIntervalID) {
                // interval of source collection is different from this collection, reset datasets
                widgetData["dataset"] = undefined;
                widgetData["intervalID"] = newIntervalID;
                widgetData["widgetData"] = undefined;
                widgetData["binsizes"] = [];
                widgetData["binsize"] = null;
                widgetData["isICCF"] = true
            }
            // update changed data in store
            this.$store.commit("compare/setWidget", widgetData);
        }
    },
    watch: {
        // watch for changes in store
        "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue, oldValue) {
                        // check if own entry changed
                        var newEntry = Object.assign({}, newValue[this.id]);
                        var oldEntry = Object.assign({}, oldValue[this.id]);
                        if (newEntry != oldEntry){
                            // entry changed, assign new child-widgets to draw
                            this.children = [];
                            for (var child of Object.values(newEntry.children)){
                                this.children.push(child)
                            }
                        // check if collection should be deleted
                        if (this.children.length == 0){
                            this.deleteCollection();
                        }
                        // reset collection to new size;
                        this.setTightBoundingArea()
                        }

                     },
        },
        selectedRegionID: function () {
            // fetch intervals and assing to windowsizes
            this.fetchData(`datasets/${this.selectedRegionID}/intervals/`).then((response) => {
                this.windowSizes = response.data;
            });
            // clear region
            this.selectedWindowSize = null;
        },
        selectedWindowSize: function() {
            // set new intervals
            var payload = {"id": this.id, "intervalID": this.selectedWindowSize};
            this.$store.commit("compare/setCollectionIntervals", payload);
        }
    },
    mounted: function() {
        // initialize from store
        var collectionData = this.$store.getters["compare/getCollectionProperties"](this.id);
        for (var child of Object.values(collectionData.children)){
            this.children.push(child)
        }
        // get datasets
        this.fetchDatasets();
    }
}
</script>

<style scoped>

.padding-top {
    padding-top: 2px;
}

.padding-right {
    padding-right: 10px;
}

.padding-left {
    padding-left: 10px;
}

.padding-bottom {
    padding-bottom: 10px;
}

.inline {
  display: inline-block;
  vertical-align: top;
}

.menu-button {
    padding-top: 10px;
    padding-right: 0px;
    padding-left: 0px;
    display: inline-block;
    vertical-align: top;
}

.md-card-header {
    padding: 0px;
}


.halfSize {
  width: 50vw;
  height: 50vh;
}

.nomargin {
    margin: 0px;
    padding: 5px;
}

</style>