<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Save Session
                <md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about addition of data</span
                        >
                    </div>
                    <div v-for="(item, index) in infoText" :key="index">
                        <span class="md-subheading">{{ item }}</span>
                    </div>
                </md-tooltip>
            </md-dialog-title>
            <addSessionForm
                @close-dialog="
                    $emit('close-dialog');
                    serializing = true;
                "
                :serializing="serializing"
            ></addSessionForm>
        </md-dialog>
    </div>
</template>

<script>
import addSessionForm from "../forms/addSessionForm";
import EventBus from "../../eventBus";

export default {
    name: "AddSessionDialog",
    data: function() {
        return {
            infoText: " \nHere you can save your sessions".split("\n"),
            serializing: true
        };
    },
    components: {
        addSessionForm
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        }
    },
    watch: {
        dialog: function(val) {
            if (val) {
                // serialize widgets when dialog is shown
                EventBus.$emit("serialize-widgets");
                // wait for serialization
                setTimeout(() => {
                    this.serializing = false;
                }, 1000);
            } else {
                this.serializing = true;
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 1000px;
}

.md-tooltip {
    height: auto;
}

.md-dialog-actions {
    display: inline;
}
</style>
