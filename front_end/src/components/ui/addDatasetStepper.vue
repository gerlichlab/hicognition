<template>
    <div>
        <md-steppers :md-active-step.sync="active" md-linear>
            <md-step
                id="first"
                md-label="Select files"
                :md-editable="false"
                :md-done.sync="first"
            >
            <selectBulkDatasetForm
                :fileTypeMapping="fileTypeMapping"
                @files-selected="handleFileSelectionSuccessful"
            ></selectBulkDatasetForm>
                <md-button
                    class="md-raised md-primary"
                    @click="setDone('first', 'second')"
                    :disabled="blockSecondStep"
                    >Continue</md-button
                >
                <md-button
                    class="md-raised md-primary"
                    @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-step>

            <md-step
                id="second"
                md-label="Add description"
                :md-editable="false"
                :md-done.sync="second"
            >
            <describeBulkDatasetForm
            :fileTypeMapping="fileTypeMapping"
            :files="selectedFiles"
            />
                <md-button
                    class="md-raised md-primary"
                    @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-step>
        </md-steppers>
    </div>
</template>

<script>
import selectBulkDatasetForm from '../forms/selectBulkDatasetForm.vue';
import describeBulkDatasetForm from "../forms/describeBulkDatasetForm.vue"

export default {
    name: "dataset-stepper",
    components: {selectBulkDatasetForm, describeBulkDatasetForm},
    props: {
        fileTypeMapping: Object
    },
    data: () => ({
        active: "first",
        first: false,
        second: false,
        blockSecondStep: true,
        selectedFiles: null
    }),
    methods: {
        handleFileSelectionSuccessful: function(files){
            console.log(files)
            this.selectedFiles = files
            this.blockSecondStep = false
            this.first = true
        },
        setDone(id, index) {
            this[id] = true;

            if (index) {
                this.active = index;
            }
        },
    }
};
</script>

<style lang="scss" scoped>

.md-stepper {
    padding: 16px 0px
}

</style>
