<template>
  <md-card md-with-hover class="higlass-card">
    <md-card-header>
      <div class="md-title">Higlass</div>
    </md-card-header>

    <md-card-content>
      <div id="higlass-browser" class="higlass"></div>
    </md-card-content>
  </md-card>
</template>

<script>
export default {
  name: "higlass-card",
  data: function() {
    return {
      higlass: null
    }
  },
  mounted(){
    this.createHiGlass()
  },
  methods: {
    createHiGlass: function () {
      this.higlass = hglib.viewer(
            document.getElementById('higlass-browser'),
            'http://higlass.io/api/v1/viewconfs/?d=default',
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

.higlass {
  width: 100%;
  height: 78vh;
}
</style>