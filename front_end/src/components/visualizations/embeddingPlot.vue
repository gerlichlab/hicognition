<template>
    <heatmap
        :stackupID="id"
        :width="width"
        :height="height"
        :stackupData="plotData"
        :minHeatmapValue="undefined"
        :maxHeatmapValue="undefined"
        :minHeatmapRange="undefined"
        :maxHeatmapRange="undefined"
        :allowValueScaleChange="true"
        colormap="red"
        :log="false"
    />
</template>

<script>
import { rectBin, select_column, flatten } from "../../functions";
import heatmap from "../visualizations/heatmap";

export default {
    name: "embeddingPlot",
    components: {
        heatmap
    },
    props: {
        rawData: Object,
        width: Number,
        height: Number,
        overlay: String
    },
    data: function() {
        return {
            id: Math.round(Math.random() * 1000000),
            size: 500
        };
    },
    computed: {
        overlayValues: function() {
            if (this.overlay == "density") {
                return undefined;
            }
            return select_column(
                this.rawData["features"]["data"],
                this.rawData["features"]["shape"],
                Number(this.overlay)
            );
        },
        points: function() {
            let embedding = this.rawData["embedding"]["data"];
            // get x and y coordinates
            let x_vals = [];
            let y_vals = [];
            for (let i = 0; i < embedding.length; i++) {
                if (i % 2 == 0) {
                    x_vals.push(embedding[i]);
                } else {
                    y_vals.push(embedding[i]);
                }
            }
            // construct plot objects
            let points = [];
            for (let j = 0; j < x_vals.length; j++) {
                let densityValue;
                if (this.overlay == "density") {
                    densityValue = 1;
                } else {
                    densityValue = this.overlayValues[j];
                }
                points.push({
                    x: x_vals[j],
                    y: y_vals[j],
                    value: densityValue
                });
            }
            return points;
        },
        plotData: function() {
            return {
                data: flatten(rectBin(this.size, this.points, this.plotBoundaries)),
                shape: [this.size, this.size],
                dtype: "float32"
            }
        },
        plotBoundaries: function() {
            let minX = Infinity;
            let maxX = -Infinity;
            let minY = Infinity;
            let maxY = -Infinity;
            for (let el of this.points) {
                if (el.x < minX) {
                    minX = el.x;
                }
                if (el.x > maxX) {
                    maxX = el.x;
                }
                if (el.y < minY) {
                    minY = el.y;
                }
                if (el.y > maxY) {
                    maxY = el.y;
                }
            }
            return {
                minX: minX,
                maxX: maxX,
                minY: minY,
                maxY: maxY
            };
        },
    },
    methods: {
    }
};
</script>
