"use strict";
const merge = require("webpack-merge");
const prodEnv = require("./prod.env");

module.exports = merge(prodEnv, {
    NODE_ENV: '"development"',
    API_URL: '"http://localhost:5000/api/"',
    STATIC_URL: '"http://localhost:5000/static/"',
    VERSION: "0.6",
    NOTIFICATION_URL: '"http://localhost:5000/stream"',
    SHOWCASE: process.env.showcase,
});
