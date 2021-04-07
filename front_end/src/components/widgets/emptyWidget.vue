<template>
    <div>
        <div
            :style="cssStyle"
            :class="emptyClass"
            @dragenter="handleDragEnter"
            @dragleave="handleDragLeave"
            @dragover.prevent
            @drop="handleDrop"
        />
    </div>
</template>

<script>
export default {
    name: "emptyWidget",
    data: function() {
        return {
            emptyClass: ["smallMargin", "empty"]
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
    computed: {
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            };
        }
    },
    methods: {
        handleDragEnter: function(e) {
            this.emptyClass.push("dark-background");
        },
        handleDragLeave: function(e) {
            this.emptyClass.pop();
        },
        handleDrop: function(event) {
            var sourceWidgetID = event.dataTransfer.getData("widget-id");
            var sourceColletionID = event.dataTransfer.getData("collection-id");
            this.emptyClass.pop();
            this.$emit(
                "widgetDrop",
                Number(sourceColletionID),
                Number(sourceWidgetID),
                this.rowIndex,
                this.colIndex
            );
        }
    }
};
</script>

<style scoped>
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
