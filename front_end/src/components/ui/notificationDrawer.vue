<template>
    <div>
        <md-toolbar class="md-accent" md-elevation="3"
            ><span class="md-title">Notifications</span>
            <div style="margin-left: auto">
                <md-button
                    class="md-icon-button"
                    @click="clearNotifications"
                    :disabled="notifications.length == 0"
                >
                    <md-icon>mark_email_read</md-icon>
                </md-button>
            </div>
        </md-toolbar>
        <md-list v-if="notifications.length != 0">
            <div v-for="item in notifications" :key="item.id">
                <component
                    :is="getNotificationComponent(item.notification_type)"
                    :item="item"
                ></component>
                <md-divider></md-divider>
            </div>
        </md-list>
        <md-empty-state
            class="md-primary"
            md-icon="done"
            md-label="You are up do date!"
            md-description="There are no notifications to display"
            v-else
        >
        </md-empty-state>
    </div>
</template>

<script>
import { mapGetters } from "vuex";
import processingFinishedNotification from "../notifications/processingFinishedNotification.vue";
import processingFailedNotification from "../notifications/processingFailedNotification.vue";
import uploadNotification from "../notifications/uploadNotification.vue";

export default {
    name: "notificationDrawer",
    components: {
        processingFinishedNotification,
        processingFailedNotification,
        uploadNotification
    },
    computed: {
        ...mapGetters(["notifications"])
    },
    methods: {
        clearNotifications: function() {
            this.$store.commit("clearNewNotifications");
        },
        getNotificationComponent: function(notificationType) {
            switch (notificationType) {
                case "processing_finished":
                    return "processingFinishedNotification";
                case "processing_failed":
                    return "processingFailedNotification";
                case "upload_notification":
                    return "uploadNotification";
                default:
                    return "processingFinishedNotification";
            }
        }
    }
};
</script>
