<template>
    <div>
        <md-toolbar class="md-accent" md-elevation="3"
            ><span class="md-title">Notifications</span>
            <div style="margin-left: auto;">
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
                <md-list-item>
                    <md-icon class="md-primary">check_circle_outline</md-icon>

                    <div class="md-list-item-text">
                        <span class="md-subheading"
                            ><span class="md-title">Dataset </span
                            >{{ item.name }}</span
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

export default {
    name: "notificationDrawer",
    computed: {
        ...mapGetters(["notifications"])
    },
    methods: {
        handleSetNotificatonRead: function(id) {
            this.$store.commit("setNotificationRead", id);
        },
        clearNotifications: function() {
            this.$store.commit("clearNewNotifications");
        }
    }
};
</script>
