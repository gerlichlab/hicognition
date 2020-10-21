/*
Collections of mixins that confer functionality to
Vue components.
*/

export var apiMixin = {
    methods: {
        fetchAndStoreToken: function (username, password) {
            /* fetches token with username ande password and stores it
            using the mutation "setToken". Returns a promise
            */
            return this.$http.post(process.env.API_URL + "tokens/", {}, {
                auth: {
                    username: username,
                    password: password
                }
            })
                .then(response => {
                    // success, store token in vuex store
                    this.$store.commit("setToken", response.data.token);
                })
        },
        fetchData: function (url) {
            /* Fetches data at url relative to api url.
            Function returns a promise. Assumes a token is stored in store.
            Redirects to login if fetching fails
            */
            // Check whether token exists
            var token = this.$store.state.token;
            if (!token) {
                // redirect to login page if token does not exist
                this.$router.push("/login");
            }
            // base64 encoding of token
            var encodedToken = btoa(token + ":");
            // fetch url
            return this.$http.get(process.env.API_URL + url, {
                headers: {
                    "Authorization": `Basic ${encodedToken}`
                }
            }).catch(error => {
                // if error is returned, redirect to login page
                this.$router.push("/login");
            })
        },
        postData: function (url, formData) {
            /*
                Will post the provided form data to the specified url.
            */
            // Check whether token exists
            var token = this.$store.state.token;
            if (!token) {
                // redirect to login page if token does not exist
                this.$router.push("/login");
            }
            // base64 encoding of token
            var encodedToken = btoa(token + ":");
            this.$http
            .post(process.env.API_URL + url, formData, {
              headers: {
                "Authorization": `Basic ${encodedToken}`,
                "Content-Type": "multipart/form-data"
              },
            }).catch(error => {
                // redirect to login upon error
                this.$router.push("/login");
            });
        }
    }
}