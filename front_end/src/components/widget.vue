<template>
<div>
    <md-card :style="cssStyle" class="smallMargin" v-if="!isEmpty"/>
    <div :style="cssStyle" class="smallMargin empty" v-else />
</div>
</template>

<script>
export default {
    name: 'widget',
    props: {
        width: Number,
        height: Number,
        empty: Boolean
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
    }
}
</script>

<style scoped>

.testSize {
    width: 300px;
    height: 300px;
}

.smallMargin {
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 2px;
    margin-bottom: 1px;
}

.empty:hover{
    background-color: grey;
    opacity: 0.5;
}



</style>