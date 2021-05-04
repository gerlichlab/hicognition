<template>
    <div class="spinner-container">
        <div style="height: 500px;" v-if="showLoad">
            <md-progress-spinner :md-diameter="400" :md-stroke="15" md-mode="indeterminate"></md-progress-spinner>
        </div>
        <div>
            <span class="md-display-1" v-if="showLoad"> Session is being restored! </span>
            <span class="md-display-1" v-else> No session token provided! </span>
        </div>
    </div>
</template>

<script>

export default {
    name: "sessionLoad",
    data: function() {
        return {
            sessionToken: null,
            sessionID: null,
            showLoad: false
        };
    },
    methods: {
        parseQueryString: function(){
            let queryObject = this.$route.query
            if ( ("sessionToken" in queryObject) && ("sessionID" in queryObject)){
                this.sessionToken = queryObject["sessionToken"],
                this.sessionID = queryObject["sessionID"]
                this.loadData()
            }
        },
        loadData: function(){
            // load session
            this.showLoad = true
        }
    },
    created: function(){
        this.parseQueryString()
    }
};
</script>

<style scoped>

.spinner-container {
    display: flex;
    justify-content: center;
    align-content: center;
    align-items: center;
    height: 800px;
    flex-direction: column;
}

</style>