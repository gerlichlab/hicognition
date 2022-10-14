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
    <!-- check if data is a list of rows -->
    <div v-if="inputType=='array'">
        <metadataField v-for="(row, index) in fieldData" :fieldData="row" :name="`meta-row-${index}`" :key="`meta-row-${index}`" @data-changed="childDataChanged"/>
    </div>
    <!-- work with dicts -->
    <div v-else>
        <div class="md-layout md-gutter">
            <template v-for="(field, name) in fieldData">
                <!-- simple text fields -->
                <template v-if="field=='freetext'">
                    <div :key="name" class="md-layout-item md-small-size-100">
                        <md-field>
                            <label :for="name">{{ camelCase(name) }}</label>
                            <md-input :name="name" :id="name" v-model="form[name]" @change="fieldChanged"/>
                        </md-field>
                    </div>
                </template>

                <!-- make a select box for simple selections -->
                <template v-else-if="Array.isArray(field)">
                    <div :key="name"  class="md-layout-item md-small-size-100">
                        <md-field>
                            <label :for="name">{{ camelCase(name) }}</label>
                            <md-select :name="name" :id="name" v-model="form[name]" @md-selected="selected(name)">
                                <md-option v-for="option in field" :key="option" :value="option">
                                    {{ option }}
                                </md-option>
                            </md-select>
                        </md-field>
                    </div>
                </template>

                <!-- make a select box that invokes further field generation -->
                <template v-else-if="typeof field === 'object'">
                    <div :key="name"  class="md-layout-item md-small-size-100">
                        <md-field>
                            <label :for="name">{{ camelCase(name) }}</label>
                            <md-select :name="name" :id="name" v-model="form[name]" @md-selected="selected(name)">
                                <md-option v-for="(option, optionName) in field" :key="optionName" :value="optionName">
                                    {{ camelCase(optionName) }}
                                </md-option>
                            </md-select>
                        </md-field>
                    </div>
                </template>
            </template>
        </div>
        <!-- placeholder for further fields -->
        <metadataField v-for="(selection, selectFieldName) in subSelections" :fieldData="selection" :name="selectFieldName" :key="selectFieldName" @data-changed="childDataChanged"/>
    </div>
</template>
<script>
import { metadataField as metadataField } from './metadataFields.vue';
export default {
  components: { metadataField },
    name: "metadataField",
    props: {
        fieldData: null
    },
    emits: [],
    data: () => ({
        form: {},
        subSelections: {}
    }),
    methods: {
        fieldChanged: function() {
            this.$emit("data-changed", JSON.parse(JSON.stringify(this.form)));
        },
        selected: function(selectFieldName) {
            this.$emit("data-changed", JSON.parse(JSON.stringify(this.form)));

            if (Array.isArray(this.fieldData[selectFieldName])) {
                return;
            }
            this.subSelections[selectFieldName] = this.fieldData[selectFieldName][this.form[selectFieldName]];
            this.$forceUpdate();
        },
        camelCase: function(text) { // https://stackoverflow.com/questions/21147832/convert-camel-case-to-human-readable-string
            if (typeof text === 'string' || text instanceof String)
            var words = text.match(/[A-Za-z][a-z]*/g) || [];
            return words.map((word) => word.charAt(0).toUpperCase() + word.substring(1)).join(" ");
        },
        hasSubSelections: function() {
            return Object.keys(this.subSelections).length > 0;
        },
        childDataChanged: function(childForm) {
            this.$emit(
                "data-changed", 
                {...JSON.parse(JSON.stringify(this.form)), ...childForm}
            );
            
        },
    },
    created: function() {
        this.inputType = Array.isArray(this.fieldData) ? "array" : typeof this.fieldData;
    }
};
</script>
