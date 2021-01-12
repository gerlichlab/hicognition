<template>
    <div>
        <div v-if="!isEmpty">
            <hicWidget v-if="this.widgetType == 'HiC'"
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

export default {
    name: 'widgetContainer',
    components: {
        emptyWidget,
        hicWidget
    },
    data: function () {
        return {
            widgetType: "HiC"
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
        propagateDrop: function() {
            // propagates widgetDrop up to widgetCollection
            // Vue events are not automatically passed on to parents https://stackoverflow.com/questions/43559561/how-to-propagate-a-vue-js-event-up-the-components-chain
           this.$emit("widgetDrop", ...arguments);
        }
    },
    computed:{
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

</style>