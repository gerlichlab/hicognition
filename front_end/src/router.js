import VueRouter from 'vue-router'
import store from "./store"

// import routes

import mainRoute from "./routes/mainRoute"
import loginRoute from "./routes/loginRoute"
import annotateRoute from "./routes/annotateRoute"
import compareRoute from "./routes/compareRoute"

// define routes

const routes = [
  { path: "/",
    redirect: "/main/compare"
  },
  { path: '/main', component: mainRoute, redirect: "/main/compare",
    meta: {
      requiresAuth: true
    },
    children : [
      {
        path: "compare", component: compareRoute,
        meta: {
           requiresAuth: true
        }
        },
      {
      path: "annotate", component: annotateRoute,
      meta: {
         requiresAuth: true
      }
      }
      ]
    },
  { path: '/login', component: loginRoute }
]

var router = new VueRouter({routes})

// handle authentication

router.beforeEach((to, from, next) => {
    if(to.matched.some(record => record.meta.requiresAuth)) {
        if (store.getters.isTokenEmpty) {
            next({
                path: '/login',
                params: { nextUrl: to.fullPath }
            })
        } else {
            next()
        }
    }else{
        next()
    }
})



export default router