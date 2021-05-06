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

                <md-tabs class="md-primary md-elevation">
                    <md-tab
                        id="tab-compare"
                        md-label="Compare"
                        to="/main/compare"
                    ></md-tab>
                    <md-tab
                        id="tab-annotate"
                        md-label="Annotate"
                        to="/main/annotate"
                    ></md-tab>
                </md-tabs>
            </div>

            <div class="md-toolbar-section-end">
                <md-menu md-size="medium" md-align-trigger>
                    <md-button md-menu-trigger>
                        <md-icon>more_vert</md-icon>
                    </md-button>

                    <md-menu-content>
                        <md-menu-item @click="$emit('add-session-click')">Save Session</md-menu-item>
                        <md-menu-item @click="$emit('my-sessions-click')">My Sessions</md-menu-item>
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
    methods: {
        logout: function() {
            this.$store.commit("clearToken")
            this.$store.commit("clearSessionToken")
            this.$globalFlags["serializeCompare"] = false
            this.$store.commit("compare/clearAll")
            this.$router.push("/login")
        }
    }
};
</script>

<style>
.span-window-horizontal {
    width: 97vw !important;
}
</style>
