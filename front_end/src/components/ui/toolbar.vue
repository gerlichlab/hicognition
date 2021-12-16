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
                <div class="md-badge-content">
                    <md-button
                        class="md-icon-button"
                        @click="$emit('showNotificationDrawer')"
                    >
                        <md-icon>notifications</md-icon>
                    </md-button>
                    <div
                        class="md-badge position-top-right md-dense red"
                        v-show="numberNotifications > 0"
                    >
                        {{ this.numberNotifications }}
                    </div>
                </div>

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

import { mapGetters } from 'vuex'

export default {
    name: "toolbar",
    data: function() {
        return {
            appversion: process.env.VERSION,
            notificationSource: null,
            notificationUrl: process.env.NOTIFICATION_URL
        };
    },
    computed: {
        numberNotifications: function() {
            return this.notifications.length;
        },
        ...mapGetters([
            'notifications'
        ])
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
            // check whether you are the issuing user
            let data = JSON.parse(event.data)
            if (data.submitted_by == this.$store.getters.getUserId){
                this.$store.commit("addNewNotification", data);
            }
        },
    },
    mounted: function() {
        this.notificationSource = new EventSource(this.notificationUrl);
        // attach event listener
        this.notificationSource.addEventListener(
            "processing_finished",
            this.handleProcessingFinished
        );
    },
    beforeDestroy: function() {
        this.notificationSource.removeEventListener(
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

.red {
    background-color: #E34234;
}

.position-top-right {
    top: 0px;
    right: 8px;
}

</style>
