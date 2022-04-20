<template>
    <div>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title
                >Add Genome Assembly
                <md-tooltip md-direction="left">
                    <div>
                        <span class="md-title"
                            >Information about addition of assemblies</span
                        >
                    </div>
                    <div class="mainText">
                        <p>
                            <span class="md-subheading">
                                In this dialog box, you can add genome
                                assemblies
                            </span>
                        </p>
                    </div>
                </md-tooltip>
            </md-dialog-title>
            <addAssemblyForm @close-dialog="$emit('close-dialog')" />
        </md-dialog>
    </div>
</template>

<script>
import addAssemblyForm from "../forms/addAssemblyForm.vue";

export default {
    name: "AddGenomeAssembly",
    components: { addAssemblyForm },
    props: {
        dialog: Boolean,
    },
    computed: {
        showDialog: function () {
            return this.dialog;
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
</style>
