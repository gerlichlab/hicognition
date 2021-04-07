<template>
    <md-card md-with-hover class="halfwidth center">
        <md-card-header>
            <div class="md-title">Annotate Datasets</div>
        </md-card-header>

        <md-card-content>
            <md-empty-state
                md-rounded
                md-icon="access_time"
                md-label="Coming soon!"
            >
            </md-empty-state>
        </md-card-content>
    </md-card>
</template>

<script>
export default {
    name: "EmptyStateRounded"
};
</script>

<style scoped>
.halfwidth {
    width: 40vw;
    height: 60v;
}

.center {
    margin: 0;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -70%);
}
</style>
