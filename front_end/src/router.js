import VueRouter from "vue-router";
import store from "./store";

// import routes

import mainRoute from "./routes/mainRoute";
import loginRoute from "./routes/loginRoute";
import registerRoute from "./routes/registerRoute"
import compareRoute from "./routes/compareRoute";
import sessionLoadRoute from "./routes/sessionLoadRoute";

// define routes

const routes = [
    { path: "/", redirect: "/main/compare" },
    {
        path: "/main",
        component: mainRoute,
        redirect: "/main/compare",
        meta: {
            requiresAuth: true
        },
        children: [
            {
                path: "compare",
                component: compareRoute,
                meta: {
                    requiresAuth: true
                }
            },
            {
                path: "session",
                component: sessionLoadRoute,
                meta: {
                    requiresAuth: true
                }
            }
        ]
    },
    { path: "/login", component: loginRoute },
    {path: "/register", component: registerRoute}
];

var router = new VueRouter({ routes });

// handle authentication

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (store.getters.isTokenEmpty) {
            next({
                path: "/login",
                query: { redirect: to.fullPath }
            });
        } else {
            next();
        }
    } else {
        next();
    }
});

export default router;
