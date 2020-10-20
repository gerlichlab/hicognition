/*
Collections of mixins that confer functionality to
Vue components.
*/

export var apiMixin = {
    methods: {
        fetchData: function (url, storeTarget) {
            /* Fetches data at url relative to api url and stores it in vuex via
            the mutation "storeTarget". e.g. /api/datasets/ could be stored via
            the mutation setDatasets via `fetchData("datasets/", "setDatasets")`.
            Function returns a promise
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
            }).then(response => {
                if (response.status != 200) {
                    console.log(`Error: ${response.data}`);
                } else {
                    // success, store datasets
                    this.$store.commit(storeTarget, response.data)
                }
            }).catch(error => {
                // if error is returned, redirect to login page
                this.$router.push("/login");
            })

        }
    }
}