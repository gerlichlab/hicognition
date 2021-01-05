<template>
  <div>
    <widget-collection class="inline top-margin" v-for="item in collections" :key="item.id" :id="item.id" @deleteCollection="handleDelete"/>
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
      currentID: 0,
      collections: [],
    };
  },
  methods: {
    handleDelete: function(removeID) {
      this.collections = this.collections.filter((element) => {
        return element.id != removeID;
      });
    },
    addCollection: function() {
      this.currentID += 1;
      this.collections.push(
        {
          id: this.currentID
        }
      )
    }
  },
  created: function() {
    // clear widgetCollections
    this.$store.commit("compare/clearWidgetCollections");
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