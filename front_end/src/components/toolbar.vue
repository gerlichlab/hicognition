<template>
  <div>
    <!-- span window horizontal is needed to position logout on the right -->
    <div class="md-toolbar-row span-window-horizontal">
      <div class="md-toolbar-section-start">
        <md-button class="md-icon-button" @click="$emit('drawer-clicked')">
          <md-icon>menu</md-icon>
        </md-button>

        <span class="md-title">HiCognition 0.1</span>
      </div>

      <div class="md-toolbar-section-end">

    <md-menu md-size="medium" md-align-trigger>
      <md-button md-menu-trigger>
        <md-icon>more_vert</md-icon>
      </md-button>

        <md-menu-content>
          <md-menu-item @click="logout">Logout</md-menu-item>
        </md-menu-content>
      </md-menu>
      </div>
    </div>

    <div class="md-toolbar-row">
      <md-tabs class="md-primary">
        <md-tab id="tab-home" md-label="Predefined" to="/main/predefined"></md-tab>
        <md-tab id="tab-pages" md-label="Annotate" to="/main/annotate"></md-tab>
        <md-tab id="tab-posts" md-label="Explore" to="/main/explore"></md-tab>
      </md-tabs>
    </div>
  </div>
</template>

<script>
export default {
  name: "toolbar",
  methods: {
    logout: function () {
      this.$store.commit("clearToken");
      this.$router.push("/login");
    }
  }
};
</script>

<style>

.span-window-horizontal {
  width: 97vw !important;
}

</style>