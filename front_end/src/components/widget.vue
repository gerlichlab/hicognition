<template>
<div>
    <div :style="cssStyle" class="smallMargin testbg" draggable="true" v-if="!isEmpty" @dragstart="handleDragStart" @dragend="handleDragEnd">
        <div class="md-layout md-gutter">
            <div class="md-layout-item md-size-30 md-horizontal-alignmment-center">
                <md-switch v-model="isCooler" class="md-primary padding-top padding-left">{{ widgetState }}</md-switch>
            </div>
            <div class="md-layout-item md-size-40">
                <md-field class="padding-top">
                        <md-select
                        v-model="selectedDataset"
                        name="dataset"
                        id="dataset"
                        placeholder="Dataset"
                        >
                        <md-option
                            v-for="item in dataset"
                            :value="item.id"
                            :key="item.id"
                            >{{ item.dataset_name }}</md-option
                        >
                        </md-select>
                </md-field>
            </div>
            <div class="md-layout-item md-size-20">
                <div class="padding-top-large">
                  <md-button  @click="deleteWidget"  class="md-icon-button md-accent">
                    <md-icon>delete</md-icon>
                 </md-button>
                </div>
            </div>
        </div>
    </div>
    <div :style="cssStyle" :class="emptyClass" v-else @dragenter="handleDragEnter" @dragleave="handleDragLeave"  @dragover.prevent @drop="handleDrop"/>
</div>
</template>

<script>
export default {
    name: 'widget',
    data: function () {
        return {
            isCooler: true,
            selectedDataset: null,
            emptyClass: ["smallMargin", "empty"],
            dataset: [
                {
                    "dataset_name": "test1",
                    "id": 1
                },
                {
                    "dataset_name": "test2",
                    "id": 2
                }
            ]
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
        text: Number
    },
    computed:{
        widgetState: function(){
            if (this.isCooler){
                return "HiC"
            }
            return "BigWig"
        },
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
        deleteWidget: function(){
            console.log("triggered");
            // delete widget from upstream collection
            this.$emit("deleteWidget", this.id);
            var payload = {
                parentID: this.collectionID,
                id: this.id
            }
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
        },
        handleDragEnd: function(e){
            if (e.dataTransfer.dropEffect != "none"){
                // successfully moved, delete element at original location
                this.deleteWidget()
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
    background-color: rgba(211, 211, 211, 0.2);
}


.no-padding-right {
    padding-right: 0px;
}

.padding-left {
    padding-left: 10px;
}

.padding-top {
    padding-top: 2px;
}

.padding-top-large {
    padding-top: 10px;
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