<template>
<div>
    <div :style="cssStyle" class="smallMargin testbg" draggable="true" v-if="!isEmpty" @dragstart="handleDragStart">
        <div class="md-layout md-gutter">
            <div class="md-layout-item md-size-35 md-horizontal-alignmment-center">
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
                            v-for="item in datasets"
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
        <div class="md-layout md-gutter">
            <div class="md-layout-item">
            <div class="padding-left">I am {{ text }}.</div>
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
            text: null,
            selectedDataset: null,
            emptyClass: ["smallMargin", "empty"],
            datasets: [
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
        toStoreObject: function(){
            // serialize object for storing its state in the store
            return {
                colIndex: this.colIndex,
                rowIndex: this.rowIndex,
                id: this.id,
                parentID: this.collectionID,
                text: this.text,
                dataset: this.selectedDataset,
                isCooler: this.isCooler
            }
        },
        deleteWidget: function(){
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id
            }
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
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
        },
        initializeWidget: function() {
            // initialize widget from store
            if (!this.empty){
                var queryObject = {
                    parentID: this.collectionID,
                    id: this.id
                };
                var widgetData = this.$store.getters["compare/getWidgetProperties"](queryObject);
                
                this.isCooler = widgetData["isCooler"];
                this.selectedDataset = widgetData["dataset"];
                this.text = widgetData["text"];
                }
            }
    },
    watch: {
        isCooler: function() {
            // is Cooler changed, signal to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
        },
        selectedDataset: function() {
            // dataset changed, signal to store
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
        }
    },
    mounted: function() {
        this.initializeWidget()
    },
    updated: function(){
        this.initializeWidget()
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