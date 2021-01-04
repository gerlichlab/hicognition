<template>
<div>
    <div :style="cssStyle" class="smallMargin testbg" v-if="!isEmpty">
        <md-card-header>
            <div class="md-title">I have id {{id}}</div>
        </md-card-header>
    </div>
    <div :style="cssStyle" class="smallMargin empty" v-else />
</div>
</template>

<script>
export default {
    name: 'widget',
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

.empty:hover{
    background-color: grey;
    opacity: 0.5;
}



</style>