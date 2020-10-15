/*
From https://stackoverflow.com/questions/48506428/nouislider-double-range-slider-with-two-inputs-vue-js
*/

<template>
  <div class="range-slider md-alignment-center-center">
    <input @change="slider" v-model.number="minValue" :min="sliderMin" :max="sliderMax" step="0.005" type="range" />
    <input @change="slider" v-model.number="maxValue" :min="sliderMin" :max="sliderMax" step="0.005" type="range" />
    <svg width="100%" height="24">
                          <line x1="4" y1="0" x2="300" y2="0" stroke="#444" stroke-width="12" stroke-dasharray="1 28"></line>
    </svg>
  </div>
</template>

<script>
export default {
    name: "dr-Slider",
    props: {
      sliderMin: Number,
      sliderMax: Number
    },
    data: function () {
        return {
            minValue: Number(this.sliderMin),
            maxValue: Number(this.sliderMax)
        }
    },
    methods: {
    slider: function() {
      this.$emit("slider-change", [this.minValue, this.maxValue])
      if (this.minValue > this.maxValue) {
        var tmp = this.maxValue;
        this.maxValue = this.minValue;
        this.minValue = tmp;
      }
    }
  },
  watch: {
    sliderMin: function (val) {
      // update to min position
      this.minValue = val;
    },
    sliderMax: function (val) {
      // update to max position
      this.maxValue = val;
    }
  }
}
</script>>

<style scoped>
.range-slider {
  width: 300px;
  margin: auto;
  text-align: center;
  position: relative;
  height: 2em;
}

.range-slider svg,
.range-slider input[type=range] {
  position: absolute;
  left: 0;
  bottom: 0;
}

input[type=number] {
  border: 1px solid #ddd;
  text-align: center;
  font-size: 1.6em;
  -moz-appearance: textfield;
}

input[type=number]::-webkit-outer-spin-button,
input[type=number]::-webkit-inner-spin-button {
  -webkit-appearance: none;
}

input[type=number]:invalid,
input[type=number]:out-of-range {
  border: 2px solid #ff6347;
}

input[type=range] {
  -webkit-appearance: none;
  width: 100%;
}

input[type=range]:focus {
  outline: none;
}

input[type=range]:focus::-webkit-slider-runnable-track {
  background: #448aff;
    border-radius: 2px;
}

input[type=range]:focus::-ms-fill-lower {
  background: #448aff;
}

input[type=range]:focus::-ms-fill-upper {
  background: #448aff;
}

input[type=range]::-webkit-slider-runnable-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  animate: 0.2s;
  background: #448aff;
  border-radius: 5px;
  box-shadow: none;
  border: 0;
}

input[type=range]::-webkit-slider-thumb {
  z-index: 2;
  position: relative;
  box-shadow: 0px 0px 0px #000;
  border: 1px solid #448aff;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #ffffff;
  cursor: pointer;
  -webkit-appearance: none;
  margin-top: -7px;
}
</style>>