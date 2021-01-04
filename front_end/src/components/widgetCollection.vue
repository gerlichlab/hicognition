<template>
    <md-card :style="cssStyle">
        <md-card-content class="nomargin">
            <widget class="inline"  v-for="item in flattenedElements" :key="item.id"
                                                      :height="item.height"
                                                      :width="item.width"
                                                      :empty="item.empty" />
        </md-card-content>
    </md-card>
</template>

<script>

import widget from "./widget"
import Widget from './widget.vue'

export default {
    name: 'widgetCollection',
    components: {
        widget
    },
    data: function () {
        return {
            marginSizeWidth: 3,
            marginSizeHeight: 3,
            paddingWidth: 18,
            paddingHeight: 20,
            collectionHeight: 300,
            collectionWidth: 600,
            children: [
                    {
                        id: 1,
                        rowIndex: 0,
                        colIndex: 0
                    },
                    {
                        id: 2,
                        rowIndex: 0,
                        colIndex: 1
                    },
                    {
                        id: 3,
                        rowIndex: 1,
                        colIndex: 1
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
        maxRowNumber: function() {
            var rowNumbers = [];
            for (var child of this.children){
                rowNumbers.push(child.rowIndex);
            }
            return Math.max(...rowNumbers);
        },
        maxColumnNumber: function() {
            var colNumbers = [];
            for (var child of this.children){
                colNumbers.push(child.colIndex);
            }
            return Math.max(...colNumbers);
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
                        empty: true
                    }
                    nextID += 1;
                }
                matrix.push(emptyRow);
            }
            console.log(matrix);
            // fill in children
            for (var child of this.children){
                matrix[child.rowIndex][child.colIndex] = {
                    id: child.id,
                        height: this.elementHeight,
                        width: this.elementWidth,
                        empty: false
                }
            }
            return matrix;
        },
        maxIDChildren: function(){
            var ids = [];
            for (var child of this.children){
                ids.push(child.id);
            }
            console.log(ids);
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
    }
}
</script>

<style scoped>

.inline {
  display: inline-block;
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