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
                <span v-if="isDemo" class="md-title">Demo &nbsp</span>
                <span v-if="!isDemo" class="md-title"
                    >{{ userName }} @ &nbsp</span
                >
                <span class="md-headline">HiCognition {{ appversion }}</span>
            </div>

            <div class="md-toolbar-section-end">
                <div class="md-badge-content">
                    <transition name="slide-fade">
                        <span
                            class="md-title"
                            style="padding: 8px; color: #264d69"
                            v-if="showDocumentationText"
                            >Documentation</span
                        >
                    </transition>
                </div>
                <div class="md-badge-content">
                    <md-button
                        class="md-icon-button no-margin"
                        @mouseenter="showDocumentationText = true"
                        @mouseleave="showDocumentationText = false"
                        href="/docs"
                    >
                        <md-icon>article</md-icon>
                    </md-button>
                </div>
                <div class="md-badge-content">
                    <md-button
                        class="md-icon-button no-margin"
                        @click="$emit('showNotificationDrawer')"
                    >
                        <md-icon>notifications</md-icon>
                    </md-button>
                    <div
                        class="md-badge position-top-right md-dense red"
                        v-show="numberNotifications > 0"
                    >
                        <span class="md-body-2">{{
                            this.numberNotifications
                        }}</span>
                    </div>
                </div>

                <md-menu md-size="medium" md-align-trigger>
                    <md-button md-menu-trigger class="md-icon-button">
                        <md-icon>more_vert</md-icon>
                    </md-button>

                    <md-menu-content>
                        <md-menu-item v-if="isDemo"
                            ><md-tooltip md-direction="top"
                                >Deactivated in demo mode</md-tooltip
                            >Save Session</md-menu-item
                        >
                        <md-menu-item
                            v-if="!isDemo"
                            @click="$emit('add-session-click')"
                            >Save Session</md-menu-item
                        >
                        <md-menu-item @click="$emit('my-sessions-click')"
                            >My Sessions</md-menu-item
                        >
                        <md-menu-item v-if="!isDemo" @click="logout"
                            >Logout</md-menu-item
                        >
                        <md-menu-item v-if="isDemo"
                            ><md-tooltip md-direction="top"
                                >No users in demo mode</md-tooltip
                            >Logout</md-menu-item
                        >
                    </md-menu-content>
                </md-menu>
            </div>
        </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
    name: "toolbar",
    data: function() {
        return {
            appversion: process.env.VERSION,
            showDocumentationText: false,
            isDemo: process.env.SHOWCASE
        };
    },
    computed: {
        numberNotifications: function() {
            return this.notifications.length;
        },
        ...mapGetters(["notifications", "userName"])
    },
    methods: {
        logout: function() {
            this.$store.commit("clearToken");
            this.$store.commit("clearSessionToken");
            this.$globalFlags["serializeCompare"] = false;
            this.$store.commit("compare/clearAll");
            this.$router.push("/login");
        },
        handleNewNotification: function(event) {
            // check whether you are the issuing user
            let data = JSON.parse(event.data);
            if (data.owner == this.$store.getters.getUserId) {
                this.$store.commit("addNewNotification", data);
            }
        }
    },
    mounted: function() {
        // attach event listener
        this.$store.state.notificationSource.addEventListener(
            "notification",
            this.handleNewNotification
        );
    },
    beforeDestroy: function() {
        this.$store.state.notificationSource.removeEventListener(
            "notification",
            this.handleNewNotification
        );
    }
};
</script>

<style>
.span-window-horizontal {
    width: 97vw !important;
}

.red {
    background-color: #e34234;
}

.position-top-right {
    top: 0px;
    right: 8px;
}

.no-margin {
    margin: 0px;
}

/*
  Enter and leave animations can use different
  durations and timing functions.
*/
.slide-fade-enter-active {
    transition: all 0.8s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-leave-active {
    transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateX(20px);
    opacity: 0;
}
</style>
