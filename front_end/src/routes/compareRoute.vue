<template>
    <div>
        <widget-collection
            class="inline top-margin"
            v-for="item in collections"
            :key="item.id"
            :id="item.id"
        />
        <div class="bottom-right">
            <md-button class="md-fab md-primary" @click="addCollection">
                <md-icon>add</md-icon>
            </md-button>
        </div>
    </div>
</template>

<script>
import widgetCollection from "../components/widgetCollection.vue";
import { apiMixin } from "../mixins";
import EventBus from "../eventBus";

export default {
    name: "CompareRoute",
    mixins: [apiMixin],
    components: {
        widgetCollection
    },
    data: function() {
        return {
            currentID: 0,
            collections: []
        };
    },
    methods: {
        fetchDatasets: function() {
            this.fetchData("datasets/").then(response => {
                // success, store datasets
                if (response){
                    this.$store.commit("setDatasets", response.data);
                }
            });
        },
        fetchResolutions: function(){
            this.fetchData("resolutions/").then(response => {
                // success, store resolutions
                if (response){
                    this.$store.commit("setResolutions", response.data)
                }
            })
        },
        addCollection: function() {
            // add newEntry to store for collection
            this.$store.commit(
                "compare/createEmptyWidgetCollection",
                this.currentID
            );
            this.currentID += 1;
        },
        updateMaxID: function() {
            var collections = Object.keys(this.$store.getters["compare/getWidgetCollections"])
            this.currentID =  Math.max(...collections) + 1;
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
                if (newEntry != oldEntry) {
                    this.collections = newEntry.map(elem => {
                        return { id: Number(elem) };
                    });
                }
            }
        }
    },
    mounted: function() {
        // initilize from store
        var collections = Object.keys(this.$store.getters["compare/getWidgetCollections"])
        this.collections = collections.map(elem => {
            return {id: Number(elem)}
        })
        // set maximum id
        if (collections.length == 0){
            this.currentID = 0
        }else{
            this.currentID = Math.max(...collections) + 1;
        }
        //
        EventBus.$on("session-loaded", this.updateMaxID)
        this.fetchDatasets()
        this.fetchResolutions()
    },
    beforeDestroy: function(){
        if (this.$globalFlags["serializeCompare"]){
            EventBus.$emit('serialize-widgets');
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
