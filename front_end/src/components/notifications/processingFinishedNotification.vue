<template>
    <md-list-item>
        <md-icon class="md-primary">check_circle_outline</md-icon>

        <div class="md-list-item-text">
            <span class="md-subheading"
                ><span class="md-title">Dataset </span>{{ item.name }}</span
            >
            <span class="md-subheading"
                ><span class="md-title">Regions </span
                >{{ item.region_name }}</span
            >
            <p>
                Processing finished!
            </p>
        </div>

        <md-button
            class="md-icon-button md-list-action"
            @click="handleSetNotificatonRead(item.id)"
        >
            <md-icon>mark_email_read</md-icon>
        </md-button>
    </md-list-item>
</template>

<script>
export default {
    name: "processingFinishedNotification",
    props: {
        item: Object
    },
    methods: {
        handleSetNotificatonRead: function(id) {
            this.$store.commit("setNotificationRead", id);
        }
    }
};
</script>
