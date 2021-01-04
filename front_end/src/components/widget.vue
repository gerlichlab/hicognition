<template>
<div>
    <div :style="cssStyle" class="smallMargin testbg" draggable="true" v-if="!isEmpty" @dragstart="handleDragStart">
        <md-card-header>
            <div class="md-title">I have id {{id}}</div>
        </md-card-header>
    </div>
    <div :style="cssStyle" :class="emptyClass" v-else @dragenter="handleDragEnter" @dragleave="handleDragLeave"/>
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
        id: Number
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
        handleDragStart: function(e) {
            console.log("started!");
            e.dataTransfer.setData('text/plain', 'dummy');
        },
        handleDragEnter: function() {
            this.emptyClass.push("dark-background")
        },
        handleDragLeave: function() {
            this.emptyClass.pop();
        }
    }
}
</script>

<style scoped>

.testbg {
    background-color: red;
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