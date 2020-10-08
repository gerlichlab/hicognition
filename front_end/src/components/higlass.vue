<template>
  <md-card md-with-hover class="higlass-card">

    <md-card-content >

            <div>
              <md-menu md-size="medium" md-align-trigger class="button-margin">
                <md-button class="md-dense md-raised md-primary" md-menu-trigger>Selected cooler</md-button>
                <md-menu-content>
                  <md-menu-item>My Item 1</md-menu-item>
                  <md-menu-item>My Item 2</md-menu-item>
                  <md-menu-item>My Item 3</md-menu-item>
                </md-menu-content>
              </md-menu>
              <md-menu md-size="medium" md-align-trigger class="button-margin">
                <md-button class="md-dense md-raised md-primary" md-menu-trigger>Selected regions</md-button>
                <md-menu-content>
                  <md-menu-item>My Item 1</md-menu-item>
                  <md-menu-item>My Item 2</md-menu-item>
                  <md-menu-item>My Item 3</md-menu-item>
                </md-menu-content>
              </md-menu>
              <md-button class="md-dense md-raised button-margin" md-menu-trigger @click="showHiglass = !showHiglass">Submit</md-button>
            </div>

            <md-divider></md-divider>

            <div id="higlass-browser" class="fill-card" ref="higlass-browser" v-show="showHiglass"></div>
            <div v-show="!showHiglass">
              <md-empty-state
              md-icon="input"
              md-label="Add a dataset"
              md-description="Once you added a dataset to the higlass browser, you can explore it"
              class="fill-card">
              </md-empty-state>
            </div>

    </md-card-content>
  </md-card>
</template>

<script>

import { getDefaultViewConf, getEmptyConf } from "../functions"

export default {
  name: "higlass-card",
  data: function() {
    return {
      higlass: null,
      showHiglass: false
    }
  },
  watch: {
    showHiglass: function (val) {
      if (val){
        // swtiched on
        this.createHiGlass()
      }else{
        // switched off
        if (this.higlass){
          this.higlass.destroy()
        }
      }
    }
  },
  methods: {
    createHiGlass: function () {
      this.higlass = hglib.viewer(
            this.$refs["higlass-browser"],
            getDefaultViewConf(),
            {
              bounded: true,
              editable: false
            }
          ); 
    }
  }
};
</script>


<style lang="scss" scoped>
.higlass-card {
  width: 65vw;
  height: 88vh;
  margin: 4px;
  display: inline-block;
  vertical-align: top;
}

.fill-card {
  width: 100%;
  height: 78vh;
}

.button-margin {
  margin: 24px;
}

</style>