/*
Collections of mixins that confer functionality to
Vue components.
*/
import EventBus from "./eventBus";
import {
    sort_matrix_by_index,
    sort_matrix_by_center_column,
    get_indices_center_column,
    mean_along_columns,
    select_column,
    select_columns,
    range
} from "./functions";

export var apiMixin = {
    methods: {
        registerUser: function(formData) {
            return this.$http
                .post(process.env.API_URL + 'register/', formData, {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                }).catch(error => {
                    if (!error.response) {
                        alert(`HTTP error: ${error}`);
                    } else {
                        // this helps to look into [object Object] errors: ${JSON.stringify(error.response)}
                        alert(
                            `HTTP error: ${error.response.status} - Error: ${error.response.data.error} - ${error.response.data.message}`
                        );
                    }
            })
        },
        fetchAndStoreDatasets: function() {
            // convenience method for fetching datasets and storing them in vuex store
            this.fetchData("datasets/").then(response => {
                if (response) {
                    // success, store datasets
                    this.$store.commit("setDatasets", response.data);
                }
            });
        },
        fetchAndStoreCollections: function() {
            // convenience method for fetching collections and storing them in vuex store
            this.fetchData("collections/").then(response => {
                if (response) {
                    // update displayed datasets
                    this.$store.commit("setCollections", response.data);
                }
            });
        },
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
                    this.$store.commit("setUserName", response.data.user_name);
                });
        },
        fetchData: function(url) {
            /* Fetches data at url relative to api url.
            Function returns a promise. Assumes a token is stored in store.
            Redirects to login if fetching fails. If there is a session token available, use it
            */
            // Check whether token exists
            var token = this.$store.state.token;
            if (!token && !process.env.SHOWCASE) {
                // redirect to login page if token does not exist
                this.$router.push("/login");
            }
            // base64 encoding of token
            var encodedToken = btoa(token + ":");
            // check whether session token exists
            var sessionToken = this.$store.getters.sessionToken;
            if (sessionToken) {
                if (url.includes("?")) {
                    url = url + `&sessionToken=${sessionToken}`;
                } else {
                    url = url + `?sessionToken=${sessionToken}`;
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
                        // check whether this is a confirmation failure
                        if (error.response.data.message.includes('Unconfirmed')) {
                            this.$router.push("/resendEmail")
                        }else{
                            // Token problem, delete it and return to login
                            this.$store.commit("clearToken");
                            this.$router.push("/login");
                        }
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
            var sessionToken = this.$store.getters.sessionToken;
            if (sessionToken) {
                if (url.includes("?")) {
                    url = url + `&sessionToken=${sessionToken}`;
                } else {
                    url = url + `?sessionToken=${sessionToken}`;
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
                        // check whether this is a confirmation failure
                        if (error.response.data.message == 'Unconfirmed') {
                            this.$router.push("/resendEmail")
                        }else{
                            // Token problem, delete it and return to login
                            this.$store.commit("clearToken");
                            this.$router.push("/login");
                        }
                    } else {
                        // this helps to look into [object Object] errors: ${JSON.stringify(error.response)}
                        alert(
                            `HTTP error: ${error.response.status} - Error: ${error.response.data.error} - ${error.response.data.message}`
                        );
                    }
                });
        },
        putData: function(url, formData) {
            /*
                Will put the provided form data to the specified url.
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
            var sessionToken = this.$store.getters.sessionToken;
            if (sessionToken) {
                if (url.includes("?")) {
                    url = url + `&sessionToken=${sessionToken}`;
                } else {
                    url = url + `?sessionToken=${sessionToken}`;
                }
            }
            return this.$http
                .put(process.env.API_URL + url, formData, {
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
                        // check whether this is a confirmation failure
                        if (error.response.data.message == 'Unconfirmed') {
                            this.$router.push("/resendEmail")
                        }else{
                            // Token problem, delete it and return to login
                            this.$store.commit("clearToken");
                            this.$router.push("/login");
                        }
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
                        // check whether this is a confirmation failure
                        if (error.response.data.message == 'Unconfirmed') {
                            this.$router.push("/resendEmail")
                        }else{
                            // Token problem, delete it and return to login
                            this.$store.commit("clearToken");
                            this.$router.push("/login");
                        }
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
        getBinSizeFormat: function(binsize) {
            let output;
            if (this.isVariableSize) {
                output = `${binsize} %`;
            } else {
                output = this.convertBasePairsToReadable(binsize);
            }
            return output;
        },
        convertBasePairsToReadable: function(baseString) {
            var basePairs = Number(baseString);
            if (Math.abs(basePairs) < 1000) {
                return basePairs + "bp";
            }
            if (Math.abs(basePairs) < 1000000) {
                return Math.round(basePairs / 1000) + " kb";
            }
            return Math.round(basePairs / 100000) / 10 + " Mb";
        }
    }
};

const TOOLBARHEIGHT = 40;
const MESSAGEHEIGHT = 50;

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
        genomicFeatureSelectionClasses: function() {
            if (this.allowBinsizeSelection) {
                return [
                    "md-layout-item",
                    "md-size-30",
                    "padding-left",
                    "padding-right"
                ];
            } else {
                return [
                    "md-layout-item",
                    "md-size-30",
                    "padding-left",
                    "padding-right"
                ];
            }
        },
        visualizationHeight: function() {
            return Math.round(this.height - TOOLBARHEIGHT - MESSAGEHEIGHT);
        },
        visualizationWidth: function() {
            return Math.round(this.width * 0.7);
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
            if (this.binsizes) {
                return Object.keys(this.binsizes).length != 0;
            }
            return false;
        },
        cssStyle: function() {
            return {
                height: `${this.height}px`,
                width: `${this.width}px`
            };
        },
        isVariableSize: function() {
            return this.intervalSize == "variable";
        }
    },
    methods: {
        blankWidget: function() {
            // removes all information that the user can set in case a certain region/dataset combination is not available
            this.widgetData = undefined;
            this.selectedDataset = undefined;
            this.selectedBinsize = undefined;
            this.widgetDataRef = undefined;
        },
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
                newCollectionData["regionID"] !=
                    oldCollectionData["regionID"] ||
                newCollectionData["intervalSize"] !=
                    oldCollectionData["intervalSize"]
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
            this.$store.commit(
                "compare/decrement_usage_dataset",
                this.selectedDataset
            );
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
            if (
                !oldCollectionConfig ||
                !this.sameCollectionConfig(
                    collectionConfig,
                    oldCollectionConfig
                )
            ) {
                return this.initializeForFirstTime(
                    widgetData,
                    collectionConfig
                );
            } else {
                return this.initializeFromStore(widgetData, collectionConfig);
            }
        }
    },
    mounted: function() {
        this.registerLifeCycleEventHandlers();
    },
    beforeDestroy: function() {
        this.removeEventHandlers();
    }
};

const EXPANSION_FACTOR = 0.2;

export var sortOrderMixin = {
    computed: {
        intervalStartBin: function() {
            if (this.widgetData) {
                let intervalSize = Math.round(
                    this.widgetData["shape"][1] / (1 + 2 * EXPANSION_FACTOR)
                );
                return Math.round(intervalSize * EXPANSION_FACTOR);
            }
            return undefined;
        },
        intervalEndBin: function() {
            if (this.widgetData) {
                let intervalSize = Math.round(
                    this.widgetData["shape"][1] / (1 + 2 * EXPANSION_FACTOR)
                );
                return (
                    intervalSize + Math.round(intervalSize * EXPANSION_FACTOR)
                );
            }
            return undefined;
        },
        sortedMatrix: function() {
            if (!this.widgetData) {
                return undefined;
            }
            if (this.selectedSortOrder == "center column") {
                var sorted_matrix = sort_matrix_by_center_column(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            } else if (this.selectedSortOrder == "region") {
                let selected = select_columns(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    range(this.intervalStartBin, this.intervalEndBin, 1)
                );
                let sort_index = mean_along_columns(
                    selected["result"],
                    selected["shape"]
                );
                var sorted_matrix = sort_matrix_by_index(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    sort_index,
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            } else if (this.selectedSortOrder == "left boundary") {
                let sort_index = select_column(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.intervalStartBin
                );
                var sorted_matrix = sort_matrix_by_index(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    sort_index,
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            } else if (this.selectedSortOrder == "right boundary") {
                let sort_index = select_column(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.intervalEndBin
                );
                var sorted_matrix = sort_matrix_by_index(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    sort_index,
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            } else {
                var sorted_matrix = sort_matrix_by_index(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.sortorders[this.selectedSortOrder],
                    this.isAscending
                );
                return {
                    data: sorted_matrix,
                    shape: this.widgetData["shape"],
                    dtype: this.widgetData["dtype"]
                };
            }
        },
        allowSortOrderSelection: function() {
            if (this.sortorders) {
                return true;
            }
            return false;
        },
        cssStyle: function() {
            let opacity = this.showSelection ? "0.6" : "1";
            // define border style
            let borderStyle;
            if (this.sortOrderRecipients > 0) {
                borderStyle = "solid";
            } else if (this.sortOrderTargetID) {
                // sort order target id is defined if widget takes sort order from somewhere else
                borderStyle = "dashed";
            } else {
                borderStyle = "none";
            }
            return {
                height: `${this.height}px`,
                width: `${this.width}px`,
                opacity: opacity,
                "box-sizing": "border-box",
                "border-width": "5px",
                "border-style": `none none ${borderStyle} none`,
                "border-color": this.sortOrderColor
                    ? this.sortOrderColor
                    : "none"
            };
        },
        sortDirection: function() {
            if (this.isAscending) {
                return "Ascending";
            }
            return "Descending";
        },
        sortKeys: function() {
            if (this.sortorders) {
                return Object.keys(this.sortorders);
            }
            return {};
        },
        allowSortOrderTargetSelection: function() {
            return (
                this.sortOrderSelectionState &&
                this.showData &&
                !this.sortOrderRecipient
            );
        }
    },
    methods: {
        broadcastSortOrderUpdate: function() {
            // tell client widgets that sort order has changed
            EventBus.$emit(
                "update-sort-order-sharing",
                this.id,
                this.constructSortOrder(),
                this.isAscending
            );
        },
        constructSortOrder: function() {
            // extracts sort order values from current selected sort-order
            let values;
            if (this.selectedSortOrder == "center column") {
                values = get_indices_center_column(
                    this.widgetData["data"],
                    this.widgetData["shape"]
                );
            } else if (this.selectedSortOrder == "region") {
                let selected = select_columns(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    range(this.intervalStartBin, this.intervalEndBin, 1)
                );
                values = mean_along_columns(
                    selected["result"],
                    selected["shape"]
                );
            } else if (this.selectedSortOrder == "left boundary") {
                values = select_column(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.intervalStartBin
                );
            } else if (this.selectedSortOrder == "right boundary") {
                values = select_column(
                    this.widgetData["data"],
                    this.widgetData["shape"],
                    this.intervalEndBin
                );
            } else {
                values = this.sortorders[this.selectedSortOrder];
            }
            return values;
        },
        manageColorUpdate: function() {
            // checks which colors are used for sort order sharing and sets a new one
            let returnedColor = this.$store.getters.getNextSortOrderColor;
            if (!returnedColor) {
                return this.colorExhaustionErrorHandler();
            } else {
                this.setBorderColor(returnedColor);
            }
        },
        colorExhaustionErrorHandler: function(kind = "sort order shares") {
            // error handler for when there are no more colors to be shared
            alert(`Maximum number of ${kind} reached!`);
            this.emitEmptySortOrderEnd();
            this.showSelection = false;
            return;
        },
        setBorderColor: function(color) {
            // sets color for widget and commits to store
            this.sortOrderColor = color;
            this.$store.commit("setColorUsage", this.sortOrderColor);
        },
        handleStartSortOrderShare: function() {
            EventBus.$emit(
                "select-sort-order-start",
                this.id,
                this.collectionID
            );
            // add event listener to window to catch next click event
            window.addEventListener("click", this.emitEmptySortOrderEnd, {
                once: true
            });
            this.expectingSortOrder = true; // this needs to be closed after receiving again -> otherwise everything updates
        },
        handleStopSortOrderShare: function() {
            // put in default
            if (this.isVariableSize) {
                this.selectedSortOrder = "region";
            } else {
                this.selectedSortOrder = "center column";
            }
            EventBus.$emit("stop-sort-order-sharing", this.sortOrderTargetID);
            this.$delete(this.sortorders, "shared");
            this.sortOrderRecipient = false;
            this.sortOrderTargetID = undefined;
        },
        emitEmptySortOrderEnd: function() {
            EventBus.$emit("select-sort-order-end", undefined, undefined);
        },
        acceptSortOrderEndEvent: function(
            target_id,
            sortorder,
            direction,
            color
        ) {
            // checks whether passed event arguments are valid and widget is in right state
            return (
                this.expectingSortOrder &&
                target_id != undefined &&
                sortorder != undefined &&
                direction != undefined &&
                color != undefined
            );
        },
        registerSortOrderClientHandlers: function() {
            // register event handlers that are relevant when widget is a sort order share client
            EventBus.$on(
                "select-sort-order-end",
                (target_id, sortorder, direction, color) => {
                    if (
                        this.acceptSortOrderEndEvent(
                            target_id,
                            sortorder,
                            direction,
                            color
                        )
                    ) {
                        // recipient stores data
                        this.$set(this.sortorders, "shared", sortorder);
                        this.selectedSortOrder = "shared";
                        this.isAscending = direction;
                        this.sortOrderTargetID = target_id;
                        this.sortOrderColor = color;
                        this.sortOrderRecipient = true;
                    }
                    this.expectingSortOrder = false; // switches off expecting recipient
                    this.sortOrderSelectionState = false; // switches off donors
                }
            );
            EventBus.$on(
                "update-sort-order-sharing",
                (target_id, sortorder, direction) => {
                    if (
                        this.sortOrderTargetID &&
                        target_id == this.sortOrderTargetID
                    ) {
                        this.$set(this.sortorders, "shared", sortorder);
                        this.selectedSortOrder = "shared";
                        this.isAscending = direction;
                    }
                }
            );
            EventBus.$on("widget-id-change", (old_id, new_id) => {
                if (
                    this.sortOrderRecipient &&
                    old_id == this.sortOrderTargetID
                ) {
                    this.sortOrderTargetID = new_id;
                }
            });
            EventBus.$on("sort-order-source-deletion", source_id => {
                if (this.sortOrderTargetID == source_id) {
                    this.handleStopSortOrderShare();
                }
            });
        },
        registerSortOrderSourceHandlers: function() {
            // handlers that are needed if widget is a sort order source
            EventBus.$on("select-sort-order-start", (id, parent_id) => {
                if (id != this.id && parent_id == this.collectionID) {
                    this.sortOrderSelectionState = true;
                }
            });
            EventBus.$on("stop-sort-order-sharing", target_id => {
                if (target_id == this.id) {
                    this.sortOrderRecipients -= 1;
                    if (this.sortOrderRecipients == 0) {
                        this.$store.commit(
                            "releaseColorUsage",
                            this.sortOrderColor
                        );
                    }
                }
            });
        },
        registerSortOrderEventHandlers: function() {
            // event bus listeners for sort order sharing
            this.registerSortOrderClientHandlers();
            this.registerSortOrderSourceHandlers();
        }
    }
};

export var valueScaleSharingMixin = {
    computed: {
        allowValueScaleChange: function() {
            if (this.valueScaleTargetID) {
                return false;
            }
            return true;
        },
        allowValueScaleTargetSelection: function() {
            return (
                this.valueScaleSelectionState &&
                this.showData &&
                !this.valueScaleRecipient
            );
        },
        valueScaleBorder: function() {
            if (this.valueScaleRecipients > 0) {
                return "solid";
            } else if (this.valueScaleTargetID) {
                return "dashed";
            }
            return undefined;
        },
        cssStyle: function() {
            let opacity = this.showSelection ? "0.6" : "1";
            return {
                height: `${this.height}px`,
                width: `${this.width}px`,
                opacity: opacity
            };
        }
    },
    methods: {
        resetColorScale: function() {
            /*
                resets colorscale to undefined
            */
            this.minHeatmap = undefined;
            this.maxHeatmap = undefined;
            this.minHeatmapRange = undefined;
            this.maxHeatmapRange = undefined;
        },
        setColorScale: function(data) {
            /* 
                sets colorScale based on data array
                containing minPos, maxPos, minRange, maxRange
            */
            this.minHeatmap = data[0];
            this.maxHeatmap = data[1];
            this.minHeatmapRange = data[2];
            this.maxHeatmapRange = data[3];
        },
        broadcastValueScaleUpdate: function() {
            // tell client widgets that value scale has changed
            if (this.valueScaleRecipients > 0) {
                EventBus.$emit(
                    "update-value-scale-sharing",
                    this.id,
                    this.minHeatmap,
                    this.maxHeatmap,
                    this.colormap,
                    this.minHeatmapRange,
                    this.maxHeatmapRange
                );
            }
        },
        manageValueScaleColorUpdate: function() {
            // checks which colors are used for value scale sharing and sets a new one
            let returnedColor = this.$store.getters.getNextValueScaleColor;
            if (!returnedColor) {
                return this.colorExhaustionErrorHandler("value scale shares");
            } else {
                this.valueScaleColor = returnedColor;
                this.$store.commit("setValueScaleColorUsage", returnedColor);
            }
        },
        handleStartValueScaleShare: function() {
            EventBus.$emit(
                "select-value-scale-start",
                this.id,
                this.$options.name // needed to check whether widget type is compatible
            );
            // add event listener to window to catch next click event
            window.addEventListener("click", this.emitEmptyValueScaleEnd, {
                once: true
            });
            this.expectingValueScale = true; // this needs to be closed after receiving again -> otherwise everything updates
        },
        handleStopValueScaleShare: function() {
            this.minHeatmap = undefined;
            this.maxHeatmap = undefined;
            this.minHeatmapRange = undefined;
            this.maxHeatmapRange = undefined;
            this.valueScaleColor = undefined;
            EventBus.$emit("stop-value-scale-sharing", this.valueScaleTargetID);
            this.valueScaleRecipient = false;
            this.valueScaleTargetID = false;
        },
        emitEmptyValueScaleEnd: function() {
            EventBus.$emit("select-value-scale-end", undefined, undefined);
        },
        acceptValueScaleEndEvent: function(
            target_id,
            min,
            max,
            color,
            minRange,
            maxRange
        ) {
            // checks whether passed event arguments are valid and widget is in right state
            return (
                this.expectingValueScale &&
                target_id != undefined &&
                min != undefined &&
                max != undefined &&
                color != undefined &&
                minRange != undefined &&
                maxRange != undefined
            );
        },
        registerValueScaleClientHandlers: function() {
            // register event handlers that are relevant when widget is value scale share client
            EventBus.$on(
                "select-value-scale-end",
                (target_id, min, max, color, colormap, minRange, maxRange) => {
                    if (
                        this.acceptValueScaleEndEvent(
                            target_id,
                            min,
                            max,
                            color,
                            minRange,
                            maxRange
                        )
                    ) {
                        // recipient stores data
                        this.valueScaleTargetID = target_id;
                        this.valueScaleColor = color;
                        this.valueScaleRecipient = true;
                        if (this.colormap != colormap) {
                            this.handleColormapMissmatch(colormap);
                        }
                        this.minHeatmap = min;
                        this.maxHeatmap = max;
                        this.minHeatmapRange = minRange;
                        this.maxHeatmapRange = maxRange;
                    }
                    this.expectingValueScale = false; // switches off expecting recipient
                    this.valueScaleSelectionState = false; // switches off donors
                }
            );
            EventBus.$on(
                "update-value-scale-sharing",
                (target_id, min, max, colormap, minRange, maxRange) => {
                    if (
                        this.valueScaleTargetID &&
                        target_id == this.valueScaleTargetID
                    ) {
                        if (this.colormap != colormap) {
                            this.handleColormapMissmatch(colormap);
                        }
                        this.minHeatmap = min;
                        this.maxHeatmap = max;
                        this.minHeatmapRange = minRange;
                        this.maxHeatmapRange = maxRange;
                    }
                }
            );
            EventBus.$on("widget-id-change", (old_id, new_id) => {
                if (
                    this.valueScaleRecipient &&
                    old_id == this.valueScaleTargetID
                ) {
                    this.valueScaleTargetID = new_id;
                }
            });
            EventBus.$on("value-scale-source-deletion", source_id => {
                if (this.valueScaleTargetID == source_id) {
                    this.handleStopValueScaleShare();
                }
            });
        },
        registerValueScaleSourceHandlers: function() {
            EventBus.$on("select-value-scale-start", (id, widgetType) => {
                if (id != this.id && this.$options.name == widgetType) {
                    this.valueScaleSelectionState = true;
                }
            });
            EventBus.$on("stop-value-scale-sharing", target_id => {
                if (target_id == this.id) {
                    this.valueScaleRecipients -= 1;
                    if (this.valueScaleRecipients == 0) {
                        this.$store.commit(
                            "releaseValueScaleColorUsage",
                            this.valueScaleColor
                        );
                        this.valueScaleColor = undefined;
                    }
                }
            });
        },
        registerValueScaleWidgetCollectionHandlers: function() {
            EventBus.$on("widget-collection-deletion", collection_id => {
                if (collection_id == this.collectionID) {
                    this.handleWidgetDeletion();
                }
            });
        },
        registerValueScaleEventHandlers: function() {
            // event bus listeners for sort order sharing
            this.registerValueScaleClientHandlers();
            this.registerValueScaleSourceHandlers();
            this.registerValueScaleWidgetCollectionHandlers();
        }
    }
};
