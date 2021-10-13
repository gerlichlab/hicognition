<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
                    <md-dialog-title
                        >Create Dataset Collection
                        <md-tooltip md-direction="left">
                            <div>
                                <span class="md-title"
                                    >Information about addition of collections</span
                                >
                            </div>
                            <div class="mainText">
                                <p>
                                    <span class="md-subheading">
                                        In this dialog box, you can select uploaded datasets to be added to a named collection.
                                        These collections are useful for calculating overlap enrichment in the  LOLA widget and 
                                        for creating low-dimensional embeddings in the Chromatin space embedding widget.
                                    </span>
                                </p>
                            </div>
                        </md-tooltip>
                    </md-dialog-title>
                <md-tabs class="md-primary">
                <md-tab id="tab-regions" md-label="Regions">
                    <addCollectionForm
                    fileType="regions"
                    @close-dialog="$emit('close-dialog')"
                    >
                    </addCollectionForm>
                </md-tab>
                <md-tab id="tab-1d-features" md-label="1d-features">
                    <addCollectionForm
                    fileType="1d-features"
                    @close-dialog="$emit('close-dialog')"
                    >
                    </addCollectionForm>
                </md-tab>
                <md-tab id="tab-2d-features" md-label="2d-features">
                    <addCollectionForm
                    fileType="2d-features"
                    @close-dialog="$emit('close-dialog')"
                    >
                    </addCollectionForm>
                </md-tab>
            </md-tabs>
        </md-dialog>
    </div>
</template>

<script>
import addCollectionForm from '../forms/addCollectionForm.vue';


export default {
    name: "CreateCollectionDialog",
    components: {addCollectionForm},
    props: {
        dialog: Boolean,
    },
    computed: {
        showDialog: function() {
            return this.dialog;
        }
    }
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
</style>
