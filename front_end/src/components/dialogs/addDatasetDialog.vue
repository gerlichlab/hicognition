<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Add Dataset
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
            <addDatasetForm
                @close-dialog="$emit('close-dialog')"
            ></addDatasetForm>
        </md-dialog>
    </div>
</template>

<script>
import addDatasetForm from "../forms/addDatasetForm";

export default {
    name: "DialogCustom",
    data: function() {
        return {
            infoText: " \nHere you can add datasets. \n Datasets can either be genomic intervals in the case of bedfiles, \n or genomic features, if you add bigwig-files or cooler files. \n\n Looking forward to your data!".split(
                "\n"
            )
        };
    },
    components: {
        addDatasetForm
    },
    props: {
        dialog: Boolean
    },
    computed: {
        showDialog: function() {
            return this.dialog;
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
