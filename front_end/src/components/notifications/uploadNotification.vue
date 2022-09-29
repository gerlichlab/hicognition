<template>
    <md-list-item class="md-expand">
        <md-icon v-if="!item.status || item.status=='success'" class="md-primary">check_circle_outline</md-icon>
        <md-icon v-else class="md-primary">error_outline</md-icon>

        <div class="md-list-item-text">
            <span class="md-subheading">
                <span class="md-title">Dataset </span>
                {{ item.dataset_name }}
            </span>
            <p v-html="item.message"></p>
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
    name: "uploadNotification",
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
