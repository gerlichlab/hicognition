<template>
    <div>
        <form
            novalidate
            class="md-layout"
            @submit.prevent="validateDataset"
            enctype="multipart/form-data"
        >
            <md-card class="md-layout-item">
                <md-card-content>
                    <div
                        class="md-layout md-gutter"
                        v-for="element in elements"
                        :set="v = $v.elements.$each[element.id]"
                        :key="element.id"
                    >
                        <div class="md-layout-item md-size-20">
                            <md-field
                            >
                                <label :for="`Filename-${element.id}`">Name</label>
                                <md-input
                                    :name="`Filename-${element.id}`"
                                    :id="`Filename-${element.id}`"
                                    :placeholder="element.filename"
                                    :disabled="true"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-field
                            :class="{ 'md-invalid': v.name.$invalid && v.name.$dirty }"
                            >
                                <label :for="`name-${element.id}`">Name</label>
                                <md-input
                                    :name="`name-${element.id}`"
                                    :id="`name-${element.id}`"
                                    v-model="element.name"
                                    :disabled="sending"
                                    required
                                />
                                <span
                                    class="md-error"
                                    v-if="!v.name.required"
                                    >A dataset name is required</span
                                >
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-field
                            >
                                <label :for="`genotype-${element.id}`">Genotype</label>
                                <md-input
                                    :name="`genotype-${element.id}`"
                                    :id="`genotype-${element.id}`"
                                    v-model="element.genotype"
                                    :disabled="sending"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-field
                            >
                                <label :for="`description-${element.id}`">Description</label>
                                <md-input
                                    :name="`description-${element.id}`"
                                    :id="`description-${element.id}`"
                                    v-model="element.descriptions"
                                    :disabled="sending"
                                />
                            </md-field>
                        </div>
                        <div class="md-layout-item md-size-20">
                            <md-checkbox
                                v-model="element.public"
                                class="top-margin"
                                >Public</md-checkbox
                            >
                        </div>
                    </div>
                </md-card-content>
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Submit dataset</md-button
                    >
                </md-card-actions>
            </md-card>
        </form>
    </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import { apiMixin } from "../../mixins";


export default {
    name: "describeBulkDatasetForm",
    mixins: [validationMixin, apiMixin],
    props: {
        files: FileList,
        fileTypeMapping: Object
    },
    data: () => ({
        datasetSaved: false,
        sending: false,
        elements: []
    }),
    computed: {
    },
    validations: {
        elements: {
            $each: {
                name: {required}
            }
        }
    },
    methods: {
        getFileType: function(filename){
            let fileEnding = filename.split(".").pop()
            return this.fileTypeMapping[fileEnding]
        },
        clearForm() {
            this.$v.$reset();
            this.elements = [];
            for (let i = 0; i < this.files.length; i++){
                var tempObject = {
                    id: i,
                    name: null,
                    genotype: null,
                    description: null,
                    filename: this.files[i].name,
                    file: this.files[i],
                    public: true
                }
                this.elements.push(tempObject)
            }
        },
        saveDataset: async function() {
            this.sending = true; // show progress bar
            // construct form data
            for (let element of this.elements){
                // construct form data
                var formData = new FormData();
                for (let key in element){
                    if (key != "id" && key != "fileanme" && key != "file"){
                        formData.append(key, element[key])
                    }
                }
                // add files
                formData.append("file", element.file, element.file.name)
                // add filetype
                formData.append("filetype", this.getFileType(element.file.name));
                // send
                await this.postData("datasets/", formData).then(response => {
                    if (!response){
                        this.sending = false;
                        return
                    }
                })
            }
            this.sending = false;
            this.datasetSaved = true;
        },
        validateDataset() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    },
    watch: {
        files: function(val){
            if (val){
                for (let i = 0; i < this.files.length; i++){
                var tempObject = {
                    id: i,
                    name: null,
                    genotype: null,
                    description: null,
                    filename: this.files[i].name,
                    file: this.files[i],
                    public: true
                }
                this.elements.push(tempObject)
            }
            }
        }
    },
};
</script>

<style lang="scss" scoped>
.md-progress-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
}
.top-margin {
    margin-top: 30px;
}


</style>
