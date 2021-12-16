<template>
    <div>
        <!-- span window horizontal is needed to position logout on the right -->
        <div class="md-toolbar-row span-window-horizontal">
            <div class="md-toolbar-section-start">
                <md-button
                    class="md-icon-button"
                    @click="$emit('drawer-clicked')"
                >
                    <md-icon>menu</md-icon>
                </md-button>
                <span class="md-title">HiCognition {{ appversion }}</span>
            </div>

            <div class="md-toolbar-section-end">
                <md-menu md-size="auto" md-align-trigger>
                    <div class="md-badge-content">
                        <md-button
                            class="md-icon-button"
                            md-menu-trigger
                            :disabled="numberNotifications == 0"
                        >
                            <md-icon>notifications</md-icon>
                        </md-button>
                        <div
                            class="md-badge md-position-top md-dense md-theme-default"
                            v-show="numberNotifications > 0"
                        >
                            {{ this.numberNotifications }}
                        </div>
                    </div>

                    <md-menu-content>
                        <md-menu-item
                            v-for="item in notifications"
                            :key="item.id"
                            @click="handleSetNotificatonRead(item.id)"
                        >
                            {{ item.name }} | {{ item.region_name }}
                            <md-icon>done</md-icon>
                        </md-menu-item>
                    </md-menu-content>
                </md-menu>

                <md-menu md-size="medium" md-align-trigger>
                    <md-button md-menu-trigger>
                        <md-icon>more_vert</md-icon>
                    </md-button>

                    <md-menu-content>
                        <md-menu-item @click="$emit('add-session-click')"
                            >Save Session</md-menu-item
                        >
                        <md-menu-item @click="$emit('my-sessions-click')"
                            >My Sessions</md-menu-item
                        >
                        <md-menu-item @click="logout">Logout</md-menu-item>
                    </md-menu-content>
                </md-menu>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "toolbar",
    data: function() {
        return {
            appversion: process.env.VERSION,
            notificationSource: null,
            notificationUrl: process.env.NOTIFICATION_URL,
            notifications: []
        };
    },
    computed: {
        numberNotifications: function() {
            return this.notifications.length;
        }
    },
    methods: {
        logout: function() {
            this.$store.commit("clearToken");
            this.$store.commit("clearSessionToken");
            this.$globalFlags["serializeCompare"] = false;
            this.$store.commit("compare/clearAll");
            this.$router.push("/login");
        },
        handleProcessingFinished: function(event) {
            this.$store.commit("addNewNotification", JSON.parse(event.data));
            this.notifications = this.$store.getters.getNewNotifications;
        },
        handleSetNotificatonRead: function(id) {
            this.$store.commit("setNotificationRead", id);
            this.notifications = this.$store.getters.getNewNotifications;
        }
    },
    mounted: function() {
        // fill in notifications
        this.notifications = this.$store.getters.getNewNotifications;
        this.notificationSource = new EventSource(this.notificationUrl);
        // attach event listener
        this.notificationSource.addEventListener(
            "processing_finished",
            this.handleProcessingFinished
        );
    }
};
</script>

<style>
.span-window-horizontal {
    width: 97vw !important;
}
</style>
