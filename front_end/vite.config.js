import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue2";
import { defineConfig } from "vite";

// The code reads its settings from process.env; these replace them when it is built. The dev
// server talks to the flask server on port 5000, a build to nginx's /flask/ location. A build
// for the demo (showcase=true in the environment) shows the publication's showcase data.
const VERSION = JSON.parse(readFileSync(new URL("./package.json", import.meta.url))).version;

function settings(dev) {
    const flask = dev ? "http://localhost:5000/" : "/flask/";
    return {
        API_URL: `${flask}api/`,
        NOTIFICATION_URL: `${flask}stream`,
        VERSION,
        SHOWCASE: process.env.showcase === "true",
        // read by the empty start page; no build sets it
        LOCAL_INSTALL: undefined,
    };
}

export default defineConfig(({ command }) => ({
    plugins: [
        vue({
            // keep the whitespace between tags, as vue-loader 13 did: the spaces between inline
            // elements such as icon buttons and radio buttons are part of the layout
            template: { compilerOptions: { whitespace: "preserve" } },
        }),
    ],
    resolve: {
        alias: [
            { find: "@", replacement: fileURLToPath(new URL("./src", import.meta.url)) },
            // webpack's prefix for imports from node_modules, as in the vue-material themes
            { find: /^~(.*)$/, replacement: "$1" },
        ],
        // the code imports .vue files without their extension
        extensions: [".mjs", ".js", ".json", ".vue"],
    },
    define: Object.fromEntries(
        Object.entries(settings(command === "serve")).map(([key, value]) => [
            `process.env.${key}`,
            value === undefined ? "undefined" : JSON.stringify(value),
        ]),
    ),
    // public/static/ becomes dist/static/, beside the built scripts and styles
    build: {
        assetsDir: "static",
        // the libraries' code in a chunk of its own, as the webpack build had it, so that a new
        // release doesn't make browsers load it again; d3, pixi.js and apexcharts make it large.
        // vue-material's styles stay with the app's: they come after the components' styles, as
        // main.js imports them, and win where both set something.
        chunkSizeWarningLimit: 2000,
        rollupOptions: {
            output: {
                manualChunks: (id) =>
                    id.includes("/node_modules/") && !/\.s?css($|\?)/.test(id) ? "vendor" : undefined,
            },
            onwarn(warning, warn) {
                // mathjs 8 places some of its #__PURE__ comments where rollup ignores them
                if (warning.code === "INVALID_ANNOTATION" && warning.id?.includes("/mathjs/")) {
                    return;
                }
                warn(warning);
            },
        },
    },
    css: {
        preprocessorOptions: {
            scss: {
                // vue-material's theme engine is written for node-sass
                quietDeps: true,
                silenceDeprecations: ["import", "global-builtin"],
            },
        },
    },
    server: {
        host: "0.0.0.0",
        port: 8080,
    },
    test: {
        include: ["src/tests/**/*.test.js"],
        globals: true,
        environment: "node",
    },
}));
