<template>
    <md-list-item>
        <md-icon class="md-primary">check_circle_outline</md-icon>

        <div class="md-list-item-text">
            <span class="md-subheading">
                <span class="md-title">Dataset </span>
                {{ item.datset_name }}
            </span>
            <span class="md-subheading"
                ><span class="md-title">Repository </span
                >{{ item.repository_name }}</span
            >
            <span class="md-subheading"
                ><span class="md-title">Sample ID </span
                >{{ item.sample_id }}</span
            >
            <p>{{ item.message }}</p>
        </div>

        <md-button
            class="md-icon-button md-list-action"
            @click="handleSetNotificatonRead(item.id)"
        >
            <md-icon v-if="item.status=='failed'">mark_email_read</md-icon>
            <md-icon v-if="item.status=='success'">mark_email_read</md-icon>
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
