/*
Collections of mixins that confer functionality to
Vue components.
*/
import EventBus from "./eventBus";

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
            // check whether session token exists
            var sessionToken = this.$store.getters.sessionToken
            if (sessionToken){
                if(url.includes("?")){
                    url = url + `&sessionToken=${sessionToken}`
                }else{
                    url = url + `?sessionToken=${sessionToken}`
                }
            }
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

const TOOLBARHEIGHT = 71;

export var widgetMixin = {
    props: {
        width: Number,
        height: Number,
        empty: Boolean,
        id: Number,
        collectionID: Number,
        rowIndex: Number,
        colIndex: Number
    },
    data: function() {
        // get widget data from store for initialization
        return this.initializeWidget();
    },
    computed: {
        visualizationHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT) * 0.8);
        },
        visualizationWidth: function() {
            return Math.round(this.width * 0.7);
        },
        sliderHeight: function() {
            return Math.round((this.height - TOOLBARHEIGHT ) * 0.07)
        },
        showData: function() {
            if (this.widgetData) {
                return true;
            }
            return false;
        },
        allowDatasetSelection: function() {
            if (this.intervalSize) {
                return true;
            }
            return false;
        },
        allowBinsizeSelection: function() {
            return Object.keys(this.binsizes).length != 0;
        },
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            };
        }
    },
    methods: {
        getCenterOfArray: function(array) {
            // returns value of center entry in array (rounded down)
            return Number(array[Math.floor(array.length / 2)]);
        },
        registerLifeCycleEventHandlers: function() {
            // registers event handlers that react to life cycle event such as deletion and serialization
            EventBus.$on("serialize-widgets", this.serializeWidget);
            // widget deletion can be trigered via event bus from widget collection
            EventBus.$on("delete-widget", id => {
                if (id == this.id) {
                    this.deleteWidget();
                }
            });
        },
        removeEventHandlers: function() {
            EventBus.$off("serialize-widgets", this.serializeWidget);
        },
        sameCollectionConfig: function(newCollectionData, oldCollectionData) {
            if (!oldCollectionData) {
                // no old data -> the widget needs to be freshly initialized
                return false;
            }
            if (
                (newCollectionData["regionID"] !=
                oldCollectionData["regionID"]) || 
                (newCollectionData["intervalSize"] !=
                oldCollectionData["intervalSize"])
            ) {
                return false;
            }
            return true;
        },
        handleDragStart: function(e) {
            // commit to store once drag starts
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
            // create data transfer object
            e.dataTransfer.setData("widget-id", this.id);
            e.dataTransfer.setData("collection-id", this.collectionID);
            // set dragimage. Dragimage dom element needs to be present before it can be passed
            // to setDragImage. Div is positioned outside of visible area for this
            this.dragImage = document.createElement("div");
            this.dragImage.style.backgroundColor = "grey";
            this.dragImage.style.height = `${this.height}px`;
            this.dragImage.style.width = `${this.width}px`;
            this.dragImage.style.position = "absolute";
            this.dragImage.style.top = `-${this.width}px`; // positioning outside of visible area
            document.body.appendChild(this.dragImage);
            e.dataTransfer.setDragImage(
                this.dragImage,
                this.height / 2,
                this.width / 2
            );
        },
        handleDragEnd: function(e) {
            // remove dragImage from document
            if (this.dragImage) {
                this.dragImage.remove();
            }
        },
        deleteWidget: function() {
            // delete widget from store
            var payload = {
                parentID: this.collectionID,
                id: this.id
            };
            // delete widget from store
            this.$store.commit("compare/deleteWidget", payload);
            // decrement dataset from used dataset in store
            this.$store.commit("compare/decrement_usage_dataset", this.selectedDataset)
        },
        serializeWidget: function() {
            var newObject = this.toStoreObject();
            this.$store.commit("compare/setWidget", newObject);
        },
        initializeWidget: function() {
            // initialize widget from store
            var queryObject = {
                parentID: this.collectionID,
                id: this.id
            };
            var widgetData = this.$store.getters["compare/getWidgetProperties"](
                queryObject
            );
            // the collection config at the current collection
            var collectionConfig = this.$store.getters[
                "compare/getCollectionConfig"
            ](this.collectionID);
            // the collection config the widget comes from
            var oldCollectionConfig = widgetData["collectionConfig"];
            if (!oldCollectionConfig || !this.sameCollectionConfig(collectionConfig, oldCollectionConfig)) {
                return this.initializeForFirstTime(
                    widgetData,
                    collectionConfig
                );
            }else{
                return this.initializeFromStore(
                    widgetData,
                    collectionConfig
                );
            }
        },
    },
    mounted: function() {
        this.registerLifeCycleEventHandlers()
    },
    beforeDestroy: function(){
        this.removeEventHandlers()
    }
}