<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >{{dialogName}}<md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about calculating associations</span
                        >
                    </div>
                    <div class="mainText">
                        <p>
                            <span class="md-subheading">
                                This form allows you to preproces collections.
                                Binsizes and windowsizes are selected
                                automatically based on reasonable presets. Happy
                                preprocessing!
                            </span>
                        </p>
                    </div>
                </md-tooltip>
            </md-dialog-title>
            <preprocessCollectionsForm
                @close-dialog="$emit('close-dialog')"
                :datatype="datatype"
            ></preprocessCollectionsForm>
        </md-dialog>
    </div>
</template>

<script>
import preprocessCollectionsForm from "../forms/preprocessCollectionsForm";

export default {
    name: "PreprocessCollectionsDialog",
    components: {
        preprocessCollectionsForm
    },
    props: {
        dialog: Boolean,
        datatype: String
    },
    computed: {
        dialogName: function(){
            if (this.datatype == "regions"){
                return "Calculate Associations"
            }else{
                return "Calculate Embeddings"
            }
        },
        showDialog: {
            set: function(value) {
                if (!value) {
                    this.$emit("close-dialog");
                }
            },
            get: function() {
                return this.dialog;
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.md-dialog /deep/.md-dialog-container {
    max-width: 1000px;
}

.mainText {
    display: block;
    width: 20vw;
    min-width: 400px;
    text-align: justify;
    text-justify: inter-word;
    word-wrap: break-word;
    white-space: normal;
}

.md-tooltip {
    height: auto;
}

.md-dialog-actions {
    display: inline;
}
</style>
