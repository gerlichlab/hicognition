<!--
This component generates textfields and checkboxes automatically based on the prop fieldData.

Rows can be specified using lists of dicts as in:
fieldData = [
    {}, <- row 1
    {}, <- row 2
    ...
],

Select-Boxes that create more fields:
fieldData = [
    {
        "AFewOptions": {
            "Colors": ["red", "green", "blue"],
            "Sizes": [1,2,3],
        }
    },
    {...},
    ...
]
-->

<template>
    <div
        v-if="isField"
        :key="fieldName"
        class="md-layout-item md-small-size-100"
    >
        <!-- simple text fields -->
        <md-field>
            <label :for="fieldName">{{ fieldName }}</label>
            <md-input
                v-if="fieldContent == 'freetext'"
                :name="fieldName"
                :id="fieldName"
                v-model="fieldValue"
                @change="changed"
            />
            <md-select
                v-else-if="Array.isArray(fieldContent)"
                :name="fieldName"
                :id="fieldName"
                v-model="fieldValue"
                @md-selected="changed"
            >
                <md-option
                    v-for="option in fieldContent"
                    :key="option"
                    :value="option"
                >
                    {{ option }}
                </md-option>
            </md-select>
            <md-select
                v-else-if="typeof fieldContent === 'object'"
                :name="fieldName"
                :id="fieldName"
                v-model="fieldValue"
                @md-selected="emitComplexSelect"
            >
                <md-option
                    v-for="(option, optionName) in fieldContent"
                    :key="optionName"
                    :value="optionName"
                >
                    {{ optionName }}
                </md-option>
            </md-select>
        </md-field>
    </div>
    <div v-else>
        <!-- check if data is a list of rows -->
        <div v-if="inputType == 'array'">
            <metadataField
                v-for="(row, index) in fieldContent"
                :fieldContent="row"
                :name="`meta-row-${index}`"
                :key="`meta-row-${index}`"
                @data-changed="pipeChanges"
            />
        </div>
        <!-- work with dicts -->
        <div v-else>
            <div class="md-layout md-gutter">
                <metadataField
                    v-for="(field, name) in fieldContent"
                    :fieldName="name"
                    :fieldContent="field"
                    isField="true"
                    :name="name"
                    :key="name"
                    @data-changed="pipeChanges"
                    @complex-select="complexSelect"
                />
            </div>
            <!-- placeholder for further fields -->
            <metadataField
                v-for="(selection, selectFieldName) in subSelections"
                :fieldContent="selection"
                :name="selectFieldName"
                :key="selectFieldName"
                @data-changed="pipeChanges"
            />
        </div>
    </div>
</template>
<script>
import metadataField from "./metadataField.vue";
export default {
    components: { metadataField },
    name: "metadataField",
    props: {
        isField: false,
        fieldName: null,
        fieldContent: null
    },
    emits: ["complex-select", "data-changed"],
    data: () => ({
        fieldValue: null,
        subSelections: {}
    }),
    methods: {
        changed: function() {
            this.$emit("data-changed", this.fieldName, this.fieldValue);
        },
        emitComplexSelect: function() {
            this.changed();
            this.$emit("complex-select", this.fieldName, this.fieldValue);
        },
        complexSelect: function(name, selection) {
            this.subSelections[name] = this.fieldContent[name][selection];
            this.$forceUpdate();
        },
        pipeChanges: function(field, value) {
            this.$emit("data-changed", field, value);
        }
    },
    created: function() {
        this.inputType = Array.isArray(this.fieldContent)
            ? "array"
            : typeof this.fieldContent;
    },
    //beforeUnmount: function() {
    beforeDestroy: function() {
        if (this.isField) {
            this.$emit("data-changed", this.fieldName, null);
        }
    }
};
</script>
