<template>
  <div>
    <b-navbar toggleable="lg" variant="primary" class="sticky-top">
    <b-navbar-nav>
        <b-nav-item>
            <b-button @click="$emit('drawer-clicked')">
            <b-icon icon="list"></b-icon>
            </b-button>
        </b-nav-item>
        <b-nav-text >
            <b-button variant="outline-secondary" disabled>
                <span v-if="isDemo" >Demo &nbsp</span>
                <span v-if="!isDemo" >{{ userName }} @ &nbsp</span>
                <span>HiCognition {{ appversion }}</span>
            </b-button>
        </b-nav-text>
    </b-navbar-nav>

      <b-navbar-nav class="ml-auto">

        <b-nav-item @click="$emit('showProcessingDrawer')">
          <b-icon icon="clock-fill"></b-icon>
          <b-badge v-if="numberProcessing > 0" variant="warning" class="position-top-right">{{ numberProcessing }}</b-badge>
        </b-nav-item>

        <b-nav-item @click="$emit('showNotificationDrawer')">
          <b-icon icon="bell-fill"></b-icon>
          <b-badge v-if="numberNotifications > 0" variant="danger" class="position-top-right">{{ numberNotifications }}</b-badge>
        </b-nav-item>

        <b-nav-item-dropdown right>
          <template #button-content>
            <b-icon icon="gear-fill"></b-icon>
          </template>
          <b-dropdown-item href="https://app.hicognition.com/docs/" target="_blank">Documentation</b-dropdown-item> 
          <b-dropdown-item v-if="!isDemo" @click="$emit('add-session-click')">Save Session</b-dropdown-item>
          <b-dropdown-item disabled v-if="isDemo">Save Session</b-dropdown-item>
          <b-dropdown-item @click="$emit('my-sessions-click')">My Sessions</b-dropdown-item>
          <b-dropdown-item v-if="!isDemo" @click="logout">Logout</b-dropdown-item>
          <b-dropdown-item disabled v-if="isDemo">Logout</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-navbar>
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
        numberProcessing: function() {
            return this.processingDatasets.length
        },
        ...mapGetters(["notifications", "userName", "processingDatasets"])
    },
    methods: {
        logout: function() {
            this.$store.commit("clearToken");
            this.$store.commit("clearSessionToken");
            this.$globalFlags["serializeCompare"] = false;
            this.$store.commit("compare/clearAll");
            this.$router.push("/login");
        },
        showProcessingDatasets: function(){
            return
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

</style>
