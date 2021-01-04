<template>
<div @dragenter="expandCollection" @dragleave="shrinkCollection">
    <md-card :style="cssStyle" ref="collectionCard">
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
                                                      @deleteWidget="handleWidgetDelete" />
        </md-card-content>
        <md-card-actions>
            <md-button @click="deleteCollection" class="md-primary">Delete</md-button>
            <md-button class="md-primary">Split</md-button>
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
            marginSizeWidth: 3,
            marginSizeHeight: 10,
            paddingWidth: 18,
            paddingHeight: 60,
            baseWidth: 300,
            baseHeight: 300,
            maxRowNumber: 0,
            maxColumnNumber: 0,
            children: [
                    {
                        id: 1,
                        rowIndex: 0,
                        colIndex: 0
                    }
            ]
        }
    },
    computed: {
        elementWidth: function() {
            return (this.collectionWidth/(this.maxColumnNumber + 1));
        },
        elementHeight: function() {
            return (this.collectionHeight/(this.maxRowNumber + 1));
        },
        collectionHeight: function() {
            return (this.maxRowNumber + 1) * this.baseHeight;
        },
        collectionWidth: function() {
            return (this.maxColumnNumber + 1) * this.baseWidth;
        },
        elementMatrix: function(){
            // creates element matrix from children that can be flattened to render with v-if
            var matrix = [];
            var nextID = this.maxIDChildren + 1;
            // create empty matrix
            for (var rowIndex = 0; rowIndex <= this.maxRowNumber; rowIndex++){
                var emptyRow = [];
                for(var colIndex = 0; colIndex <= this.maxColumnNumber; colIndex++){
                    emptyRow[colIndex] = {
                        id: nextID,
                        height: this.elementHeight,
                        width: this.elementWidth,
                        empty: true,
                        rowIndex: rowIndex,
                        colIndex: colIndex
                    }
                    nextID += 1;
                }
                matrix.push(emptyRow);
            }
            // fill in children
            for (var child of this.children){
                matrix[child.rowIndex][child.colIndex] = {
                    id: child.id,
                        height: this.elementHeight,
                        width: this.elementWidth,
                        empty: false,
                        rowIndex: child.rowIndex,
                        colIndex: child.colIndex
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
            if (e.toElement == this.$refs["collectionCard"].$el){
                this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
                this.maxColumnNumber = Math.max(...this.children.map((element) => element.colIndex));
            }
        },
        deleteCollection: function() {
            this.$emit("deleteCollection", this.id);
        },
        handleWidgetDrop: function(sourceColletionID, sourceWidgetID, rowIndex, colIndex) {
            // here, data from widget needs to be obtained from store. TODO
            this.children.push({
                id: this.maxIDChildren + 1,
                rowIndex: rowIndex,
                colIndex: colIndex
            });
            // reset indices to new value;
            this.maxRowNumber = Math.max(...this.children.map((element) => element.rowIndex));
            this.maxColumnNumber =  Math.max(...this.children.map((element) => element.colIndex));
        }
    }
}
</script>

<style scoped>

.inline {
  float: left;
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