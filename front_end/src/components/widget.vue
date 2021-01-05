<template>
<div>
    <div :style="cssStyle" class="smallMargin testbg" draggable="true" v-if="!isEmpty" @dragstart="handleDragStart" @dragend="handleDragEnd">
            <div class="md-title text">I have id {{id}}</div>
    </div>
    <div :style="cssStyle" :class="emptyClass" v-else @dragenter="handleDragEnter" @dragleave="handleDragLeave"  @dragover.prevent @drop="handleDrop"/>
</div>
</template>

<script>
export default {
    name: 'widget',
    data: function () {
        return {
            emptyClass: ["smallMargin", "empty"]
        }
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
    computed:{
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            }
        },
        isEmpty: function() {
            if (this.empty == true){
                return true;
            }else{
                return false;
            }
        }
    },
    methods: {
        handleDragEnd: function(e){
            if (e.dataTransfer.dropEffect != "none"){
                // successfully moved, delete element at original location
                this.$emit("deleteWidget", this.id)
            }
        },
        handleDragStart: function(e) {
            e.dataTransfer.setData('widget-id', this.id);
            e.dataTransfer.setData("collection-id", this.collectionID);
        },
        handleDragEnter: function(e) {
            this.emptyClass.push("dark-background")
        },
        handleDragLeave: function(e) {
            this.emptyClass.pop();
        },
        handleDrop: function(event) {
            var sourceWidgetID = event.dataTransfer.getData("widget-id");
            var sourceColletionID = event.dataTransfer.getData("collection-id");
            this.emptyClass.pop();
            this.$emit("widgetDrop", Number(sourceColletionID), Number(sourceWidgetID), this.rowIndex, this.colIndex);
        }
    }
}
</script>

<style scoped>

.testbg {
    background-color: red;
}


.text {
    display: flex;
    justify-content: left;
    align-items: center;
    padding: 10px;
}

.smallMargin {
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 2px;
    margin-bottom: 1px;
}

.dark-background {
    background-color: grey;
    opacity: 0.5;
}

</style>