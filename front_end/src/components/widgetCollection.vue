<template>
<div @dragenter="expandCollection" @dragleave="shrinkCollection">
    <md-card :style="cssStyle" ref="collectionCard">
        <md-card-header>
            <div class="md-layout md-gutter">
                <div class="md-layout-item md-size-40">
                    <div class="menu-button">
                        <md-button @click="handleZoomIn" class="md-icon-button">
                            <md-icon>zoom_in</md-icon>
                        </md-button>
                    </div>
                    <div class="menu-button">
                        <md-button @click="handleZoomOut" class="md-icon-button">
                            <md-icon>zoom_out</md-icon>
                        </md-button>
                    </div>
                </div>
                <div class="md-layout-item md-size-45">
                    <md-field>
                    <label for="region">Region</label>
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
            </div>
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
                                                      @widgetDrop="handleWidgetDrop"
                                                      @deleteWidget="handleWidgetDelete"
                                                      :text="item.text" />
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

export default {
    name: 'widgetCollection',
    props: {
        id: Number
    },
    components: {
        widget
    },
    data: function () {
        return {
            regions: [
                {
                    id: 0,
                    dataset_name: "test1"
                },
                {
                    id: 1,
                    dataset_name: "test2"
                }
            ]
            ,
            selectedRegionID: null,
            marginSizeWidth: 3,
            marginSizeHeight: 10,
            paddingWidth: 18,
            paddingHeight: 130,
            baseWidth: 300,
            baseHeight: 300,
            maxRowNumber: 0,
            maxColumnNumber: 0,
            children: [
                    {
                        id: 1,
                        rowIndex: 0,
                        colIndex: 0,
                        text: Math.floor(Math.random() * 100),
                        parentID: this.id
                    }
            ]
        }
    },
    computed: {
        collectionHeight: function() {
            return (this.maxRowNumber + 1) * this.baseHeight;
        },
        collectionWidth: function() {
            return (this.maxColumnNumber + 1) * this.baseWidth;
        },
        elementMatrix: function(){
            // creates element matrix from children filled up with empty elements
            var matrix = [];
            var nextID = this.maxIDChildren + 1;
            // create empty matrix
            for (var rowIndex = 0; rowIndex <= this.maxRowNumber; rowIndex++){
                var emptyRow = [];
                for(var colIndex = 0; colIndex <= this.maxColumnNumber; colIndex++){
                    emptyRow[colIndex] = {
                        id: nextID,
                        height: this.baseHeight,
                        width: this.baseWidth,
                        empty: true,
                        rowIndex: rowIndex,
                        colIndex: colIndex,
                        parentID: this.id
                    }
                    nextID += 1;
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
        maxIDChildren: function(){
            var ids = [];
            for (var child of this.children){
                ids.push(child.id);
            }
            return Math.max(...ids)
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
        handleZoomIn: function() {
            this.baseWidth += 50;
            this.baseHeight += 50;
        },
        handleZoomOut: function() {
            this.baseWidth -= 50;
            this.baseHeight -= 50;
        },
        handleWidgetDelete: function(id) {
            this.children = this.children.filter((el) => {
                return el.id != id
            });
            // reset indices to new value;
            this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
            this.maxColumnNumber =  Math.max(...this.children.map((element) => element.colIndex));
            // check if collection should be deleted
            if (this.children.length == 0){
                this.$emit("deleteCollection", this.id);
                //this.$store.commit("compare/deleteWidgetCollection", this.id);
            }
        },
        expandCollection: function(){
            var maxRowElements = Math.max(...this.children.map((element) => element.rowIndex));
            var maxColElements = Math.max(...this.children.map((element) => element.colIndex));
            this.maxRowNumber = maxRowElements + 1;
            this.maxColumnNumber = maxColElements + 1;
        },
        shrinkCollection: function(e) {
            // check if card is collection card, all child elements trigger leave events
            if ((e.toElement == this.$refs["collectionCard"].$el) || (e.toElement.contains(this.$refs["collectionCard"].$el))){
                this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
                this.maxColumnNumber = Math.max(...this.children.map((element) => element.colIndex));
            }
        },
        deleteCollection: function() {
            this.$emit("deleteCollection", this.id); // notify compare view to remove this collection
            this.$store.commit("compare/deleteWidgetCollection", this.id);
        },
        handleWidgetDrop: function(sourceColletionID, sourceWidgetID, rowIndex, colIndex) {
            // if parentID was same as source ID, just update row and columns. This cannot be handled by events since the receiving element of dragend vanishes.
            if (sourceColletionID == this.id){
                var currentChild = this.children.find((el) => el.id == sourceWidgetID);
                // delete old entry from store
                this.$store.commit("compare/deleteWidget", {"id": currentChild.id, "parentID": this.id});
                // increment id and update row and columns
                currentChild["id"] = this.maxIDChildren + 1;
                currentChild["rowIndex"] = rowIndex;
                currentChild["colIndex"] = colIndex;
                // update store with new properties
                var payload = Object.assign({}, currentChild);
                this.$store.commit("compare/setWidget", payload);
                // restore size of collection
                this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
                this.maxColumnNumber =  Math.max(...this.children.map((element) => element.colIndex));
            }else{
                // obtain data from store
                var queryObject = {
                    parentID: sourceColletionID,
                    id: sourceWidgetID
                };
                var widgetData = this.$store.getters["compare/getWidgetProperties"](queryObject);
                // update changed data in the collection
                widgetData["id"] = this.maxIDChildren + 1;
                widgetData["rowIndex"] = rowIndex;
                widgetData["colIndex"] = colIndex;
                widgetData["parentID"] = this.id;
                this.children.push(widgetData);
                // update changed data in store
                this.$store.commit("compare/setWidget", widgetData);
                // reset indices to new value;
                this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
                this.maxColumnNumber =  Math.max(...this.children.map((element) => element.colIndex));
            }
        }
    },
    mounted: function() {
        // add self to store. Has only one child at init
        var payload = Object.assign({}, this.children[0]);
        payload["parentID"] = this.id;
        this.$store.commit("compare/setWidgetCollection", payload);
    }
}
</script>

<style scoped>

.inline {
  display: inline-block;
  vertical-align: top;
}

.menu-button {
    padding-top: 16px;
    padding-right: 0px;
    padding-left: 0px;
    display: inline-block;
    vertical-align: top;
}

.md-card-header {
    padding: 0px;
}

.md-layout-item {
    padding-right: 2px;
    padding-left: 2px;
}

.md-layout-gutter {
    padding-right: 2px;
    padding-left: 2px;
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