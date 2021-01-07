<template>
  <div>
    <widget-collection class="inline top-margin" v-for="item in collections" :key="item.id" :id="item.id" />
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
    addCollection: function() {
      // add newEntry to store for collection with a single child
      var initialChild = {
                      id: 1,
                      rowIndex: 0,
                      colIndex: 0,
                      text: Math.floor(Math.random() * 100),
                      parentID: this.currentID,
                      isCooler: true,
                      dataset: null
                  };
        this.$store.commit("compare/setWidgetCollection", initialChild);
      this.currentID += 1;
    }
  },
  watch: {
      // watch for changes in store -> compare route only needs to check which collections to render
      "$store.state.compare.widgetCollections": {
            deep: true,
            handler: function(newValue, oldValue) {
                        // check if own entry changed
                        var newEntry = Object.keys(newValue);
                        var oldEntry = Object.keys(oldValue);
                        if (newEntry != oldEntry){
                            this.collections = newEntry.map((elem) => {
                              return {id: Number(elem)}
                            });
                          }
                        }
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