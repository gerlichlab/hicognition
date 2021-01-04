<template>
  <div>
    <widget-collection class="inline top-margin" v-for="item in collections" :key="item.id" />
    <div class="bottom-right">
      <md-button class="md-fab md-primary" @click="addCollection">
          <md-icon>add</md-icon>
      </md-button>
    </div>
  </div>
</template>

<script>
import widgetCollection from "../components/widgetCollection.vue";

export default {
  name: "CompareRoute",
  components: {
    widgetCollection,
  },
  data: function () {
    return {
      collections: [
        {
          id: 1,
        }
      ],
    };
  },
  computed: {
    maxID: function() {
      var ids = [];
      for (var collection of this.collections){
        ids.push(collection.id);
      }
      return Math.max(...ids);
    }
  },
  methods: {
    addCollection: function() {
      this.collections.push(
        {
          id: this.maxID + 1
        }
      )
    }
  }
};
</script>

<style scoped>
.inline {
  display: inline-block;
}
.bottom-right {
  position: fixed;
  right: 10vw;
  bottom: 10vh;
  z-index: 999;
}
.top-margin {
  margin-top: 10px;
}
</style>