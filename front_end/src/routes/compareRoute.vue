<template>

<widget-collection/>

</template>

<script>

import widgetCollection from '../components/widgetCollection'
import WidgetCollection from '../components/widgetCollection.vue'

export default {
    name: 'CompareRoute',
    components: {
      widgetCollection
    }
}

</script>

<style scoped>

.inline {
  display: inline-block;
}
</style>