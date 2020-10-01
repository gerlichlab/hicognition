import VueRouter from 'vue-router'

// import routes

import mainRoute from "./routes/mainRoute"
import loginRoute from "./routes/loginRoute"
import predefinedRoute from "./routes/predefinedRoute"
import annotateRoute from "./routes/annotateRoute"
import exploreRoute from "./routes/exploreRoute"

// define routes

const routes = [
  { path: '/main', component: mainRoute,
    meta: {
      requiresAuth: true
    },
    children : [{
      path: "predefined", component: predefinedRoute,
      meta: {
         requiresAuth: true
      }
      },
      {
      path: "explore", component: exploreRoute,
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
        if (localStorage.getItem('token') == null) {
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