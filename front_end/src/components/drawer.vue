<template>
<div>
    <md-toolbar class="md-transparent" md-elevation="0">Navigation</md-toolbar>
    <md-list>
      <md-list-item>
        <md-icon>move_to_inbox</md-icon>
        <span class="md-list-item-text">Add Datasets</span>
      </md-list-item>

      <md-list-item>
        <md-icon>send</md-icon>
        <span class="md-list-item-text">Derived Datasets</span>
      </md-list-item>

      <md-list-item>
        <md-icon>delete</md-icon>
        <span class="md-list-item-text">Precompute Datasets</span>
      </md-list-item>
    </md-list>
</div>
</template>

<script>
export default {
  name: "drawer",
};
</script>