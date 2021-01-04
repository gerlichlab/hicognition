<template>
  <div>
    <widget-collection class="inline top-margin" v-for="item in collections" :key="item.id" :id="item.id" @deleteCollection="handleDelete" />
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
      // check if there is an element in the collection
      if (this.collections.length == 0){
        return 0;
      }
      var ids = [];
      for (var collection of this.collections){
        ids.push(collection.id);
      }
      return Math.max(...ids);
    }
  },
  methods: {
    handleDelete: function(removeID) {
      this.collections = this.collections.filter((element) => {
        return element.id != removeID;
      });
    },
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