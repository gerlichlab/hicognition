/*
Collections of mixins that confer functionality to
Vue components.
*/

export var apiMixin = {
    methods: {
        fetchAndStoreToken: function(username, password) {
            /* fetches token with username ande password and stores it
            using the mutation "setToken". Returns a promise
            */
            return this.$http
                .post(
                    process.env.API_URL + "tokens/",
                    {},
                    {
                        auth: {
                            username: username,
                            password: password
                        }
                    }
                )
                .then(response => {
                    // success, store token in vuex store
                    this.$store.commit("setToken", response.data.token);
                    this.$store.commit("setUserId", response.data.user_id);
                });
        },
        fetchData: function(url) {
            /* Fetches data at url relative to api url.
            Function returns a promise. Assumes a token is stored in store.
            Redirects to login if fetching fails. If there is a session token available, use it
            */
            // Check whether token exists
            var token = this.$store.state.token;
            if (!token) {
                // redirect to login page if token does not exist
                this.$router.push("/login");
            }
            // base64 encoding of token
            var encodedToken = btoa(token + ":");
            // check whether session token exists
            var sessionToken = this.$store.getters.sessionToken
            if (sessionToken){
                if(url.includes("?")){
                    url = url + `&sessionToken=${sessionToken}`
                }else{
                    url = url + `?sessionToken=${sessionToken}`
                }
            }
            // fetch url
            return this.$http
                .get(process.env.API_URL + url, {
                    headers: {
                        Authorization: `Basic ${encodedToken}`
                    }
                })
                .catch(error => {
                    if (!error.response) {
                        alert(`HTTP error: ${error}`);
                    } else if (
                        error.response.status == 403 ||
                        error.response.status == 401
                    ) {
                        // if forbidden error is returned, delete token and return to login
                        this.$store.commit("clearToken");
                        this.$router.push("/login");
                    } else {
                        alert(
                            `HTTP error: ${error.response.status} - Error: ${error.response.data.error} - ${error.response.data.message}`
                        );
                    }
                    // TODO: 401 error writes unknown - unknown make and else for data.error os unknown
                });
        },
        postData: function(url, formData) {
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
            return this.$http
                .post(process.env.API_URL + url, formData, {
                    headers: {
                        Authorization: `Basic ${encodedToken}`,
                        "Content-Type": "multipart/form-data"
                    }
                })
                .catch(error => {
                    if (!error.response) {
                        alert(`HTTP error: ${error}`);
                    } else if (
                        error.response.status == 403 ||
                        error.response.status == 401
                    ) {
                        // if forbidden error is returned, redirect to login page
                        this.$router.push("/login");
                    } else {
                        // this helps to look into [object Object] errors: ${JSON.stringify(error.response)}
                        alert(
                            `HTTP error: ${error.response.status} - Error: ${error.response.data.error} - ${error.response.data.message}`
                        );
                    }
                });
        },
        deleteData: function(url) {
            /*
                Will make a delete call to the specified url.
            */
            // Check whether token exists
            var token = this.$store.state.token;
            if (!token) {
                // redirect to login page if token does not exist
                this.$router.push("/login");
            }
            // base64 encoding of token
            var encodedToken = btoa(token + ":");
            return this.$http
                .delete(process.env.API_URL + url, {
                    headers: {
                        Authorization: `Basic ${encodedToken}`
                    }
                })
                .catch(error => {
                    if (!error.response) {
                        alert(`HTTP error: ${error}`);
                    } else if (
                        error.response.status == 403 ||
                        error.response.status == 401
                    ) {
                        // if forbidden error is returned, redirect to login page
                        this.$router.push("/login");
                    } else {
                        alert(
                            `HTTP error: ${error.response.status} - Error: ${error.response.data.error} - ${error.response.data.message}`
                        );
                    }
                });
        }
    }
};

export var formattingMixin = {
    methods: {
        convertBasePairsToReadable: function(baseString) {
            var basePairs = Number(baseString);
            if (basePairs < 1000) {
                return basePairs + "bp";
            }
            if (basePairs < 1000000) {
                return Math.round(basePairs / 1000) + " kb";
            }
            return Math.round(basePairs / 1000000) + " Mb";
        }
    }
};
