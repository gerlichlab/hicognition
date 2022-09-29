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
                    @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-step>

            <md-step
                id="second"
                md-label="Name and genome"
                :md-editable="false"
                :md-done.sync="second"
            >
                <step2BulkDatasetForm
                    :fileTypeMapping="fileTypeMapping"
                    :files="selectedFiles"
                    @step-completion="
                        handleStepCompletion($event, 'second', 'third')
                    "
                />
                <md-button
                    class="md-raised md-primary"
                    @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-step>
            <md-step
                id="third"
                md-label="Conditions"
                :md-editable="false"
                :md-done.sync="third"
            >
                <step-3-bulk-dataset-form
                    :fileInformation="elements"
                    :fileTypeMapping="fileTypeMapping"
                    @step-completion="
                        handleStepCompletion($event, 'third', 'fourth')
                    "
                />
                <md-button
                    class="md-raised md-primary"
                    @click="$emit('close-dialog')"
                    >Close</md-button
                >
            </md-step>
            <md-step
                id="fourth"
                md-label="Technical information"
                :md-editable="false"
                :md-done.sync="fourth"
            >
                <step-4-bulk-dataset-form
                    :fileInformation="elements"
                    :fileTypeMapping="fileTypeMapping"
                    v-if="third"
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
import selectBulkDatasetForm from "../forms/selectBulkDatasetForm.vue";
import step2BulkDatasetForm from "../forms/step2BulkDatasetForm.vue";
import step3BulkDatasetForm from "../forms/step3BulkDatasetForm.vue";
import step4BulkDatasetForm from "../forms/step4BulkDatasetForm.vue";

export default {
    name: "dataset-stepper",
    components: {
        selectBulkDatasetForm,
        step2BulkDatasetForm,
        step3BulkDatasetForm,
        step4BulkDatasetForm
    },
    props: {
        fileTypeMapping: Object
    },
    data: () => ({
        active: "first",
        first: false,
        second: false,
        third: false,
        fourth: false,
        selectedFiles: null,
        elements: undefined
    }),
    methods: {
        handleFileSelectionSuccessful: function(files) {
            this.selectedFiles = files;
            this.first = true;
            this.setDone("first", "second");
        },
        handleStepCompletion: function(elements, currentStep, nextStep) {
            if (!this.elements) {
                this.elements = elements;
            } else {
                for (let [id, value] of Object.entries(elements)) {
                    this.elements[id] = value;
                }
            }
            this.setDone(currentStep, nextStep);
        },
        setDone(id, index) {
            this[id] = true;

            if (index) {
                this.active = index;
            }
        }
    }
};
</script>

<style lang="scss" scoped>
.md-stepper {
    padding: 16px 0px;
}
</style>
