import { defaultConf, emptyConfLocal } from "./config_templates"

export default function generateData(count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
        var x = 'w' + (i + 1).toString();
        var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

        series.push({
            x: x,
            y: y
        });
        i++;
    }
    return series;
}

export function getDefaultViewConf() {
    // Returns default config file for Higlass using higlass.io as a source server
    return defaultConf
}

export function getEmptyConf() {
    // Returns empty config file for local Higlass server. URL is defined in config/dev.env.js
    return emptyConfLocal
}
