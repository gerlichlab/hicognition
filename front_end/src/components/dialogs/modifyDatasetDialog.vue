<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>Edit Dataset </md-dialog-title>
            <md-content class="content">
                <modify-dataset-form
                    :datasetID="datasetID"
                    @close-dialog="$emit('close-dialog')"
                />
            </md-content>
            <md-dialog-actions>
                <md-button class="md-secondary" @click="$emit('close-dialog')"
                    >Close</md-button
                >
                <div class="float-right" v-if="isBedFile">
                    <md-button class="md-primary" @click="downloadData">
                        Download
                    </md-button>
                </div>
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>

<script>
import modifyDatasetForm from "../forms/modifyDatasetForm.vue";
import { apiMixin } from "../../mixins";

export default {
    name: "EditDatasetDialog",
    components: { modifyDatasetForm },
    mixins: [apiMixin],
    props: {
        dialog: Boolean,
        datasetID: Number,
    },
    data: function () {
        return {
            dataset: undefined,
        };
    },
    computed: {
        showDialog: function () {
            return this.dialog;
        },
        isBedFile: function () {
            if (!this.dataset) {
                return false;
            }
            return this.dataset.filetype == "bedfile";
        },
    },
    methods: {
        getDatasetFromStore: function () {
            this.dataset = this.$store.getters["getDataset"](this.datasetID);
        },
        downloadData: async function () {
            let csv = "";
            const blarray = await this.fetchBed();
            blarray.forEach((row) => {
                const colarray = Object.values(row);
                csv += colarray.join("\t");
                csv += "\n";
            });
            const encodedUri = encodeURI(csv);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute(
                "href",
                "data:text/csv;charset=utf-8,%EF%BB%BF" + encodeURI(csv)
            );
            let datasetName = await this.fetchName();
            link.setAttribute("download", `${datasetName}.bed`);
            document.body.appendChild(link);
            link.click();
        },
        fetchName: async function () {
            let name = await this.fetchData(`datasets/${this.datasetID}/name/`);
            return name.data;
        },
        fetchBed: async function () {
            let response = await this.fetchData(
                `datasets/${this.datasetID}/bedFile/`
            );
            return Object.values(response.data);
        },
    },
    watch: {
        dialog: function (val) {
            if (val) {
                this.getDatasetFromStore();
            }
        },
    },
};
</script>

<style lang="scss" scoped>
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

.float-right {
    float: right;
}
</style>
