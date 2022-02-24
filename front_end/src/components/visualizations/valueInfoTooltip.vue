<template>
    <div :style="tooltipStyle">
        {{ message }}
    </div>
</template>

<script>
export default {
    name: "ValueTooltip",
    props: {
        message: String,
        tooltipOffsetLeft: Number,
        tooltipOffsetTop: Number
    },
    data: function() {
        return {
            tooltipStyle: {
                position: "absolute",
                "background-color": "black",
                top: `${this.tooltipOffsetTop}px`,
                left: `${this.tooltipOffsetLeft}px`,
                "z-index": "10",
                "pointer-events": "none",
                "opacity": "0.7",
                "border-radius": "5px",
                "padding": "5px",
                "min-width": "150px",
                "color": "white"
            }
        };
    },
    watch: {
        tooltipOffsetLeft: function(val) {
            this.tooltipStyle["left"] = `${val}px`;
        },
        tooltipOffsetTop: function(val) {
            this.tooltipStyle["top"] = `${val}px`;
        }
    }
};
</script>
