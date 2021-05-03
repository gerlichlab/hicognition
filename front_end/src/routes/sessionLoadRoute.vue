<template>
    <div class="spinner-container">
        <div style="height: 500px;">
            <md-progress-spinner :md-diameter="400" :md-stroke="15" md-mode="indeterminate"></md-progress-spinner>
        </div>
        <div>
            <span class="md-display-1"> Session is being restored! </span>
        </div>
    </div>
</template>

<script>

export default {
    name: "sessionLoad",
    data: function() {
        return {
            currentID: 0,
            collections: []
        };
    }
};
</script>

<style scoped>

.spinner-container {
    display: flex;
    justify-content: center;
    align-content: center;
    align-items: center;
    height: 800px;
    flex-direction: column;
}

</style>