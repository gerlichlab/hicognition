<template>
<b-container class="container">
    <b-row fluid class="flex-grow-1 d-flex align-items-center justify-content-center">
        <b-col  md="6" lg="4" cols="5">
        <b-form @submit="validateDataset">
        <b-card no-body>
            <b-card-header>
                    <h4 class="mb-0">Register</h4>
            </b-card-header>

            <b-card-body>
            <!-- Username -->
            <b-form-group
                label="Username"
                label-for="userName"
                :state="getValidationState('userName')"
                invalid-feedback="Username needs to be within 3 and 80 characters"
            >
                <b-form-input
                id="userName"
                v-model="form.userName"
                :state="getValidationState('userName')"
                ></b-form-input>
            </b-form-group>
            <!-- Email Address -->
            <b-form-group
                label="Email address"
                label-for="emailAddress"
                :state="getValidationState('emailAddress')"
                invalid-feedback="Not a valid format"
            >
                <b-form-input
                id="emailAddress"
                v-model="form.emailAddress"
                :state="getValidationState('emailAddress')"
                ></b-form-input>
            </b-form-group>
            <!-- Password 1 -->
            <b-form-group
                label="Password"
                label-for="password1"
                :state="getValidationState('password1')"
                invalid-feedback="At least 5 characters!"
            >
                <b-form-input
                id="password2"
                v-model="form.password1"
                :state="getValidationState('password1')"
                type="password"
                ></b-form-input>
            </b-form-group>
            <!-- Password 2 -->
            <b-form-group
                label="Confirm password"
                label-for="password2"
                :state="getValidationState('password2')"
                invalid-feedback="Passwords need to be equal"
            >
                <b-form-input
                id="password2"
                v-model="form.password2"
                :state="getValidationState('password2')"
                type="password"
                ></b-form-input>
            </b-form-group>
            </b-card-body>

            <b-card-footer>
            <b-button type="submit" variant="primary">Create user</b-button>
            <b-tooltip target="create-user" triggers="hover" placement="top">
                Public registration will be available soon!
            </b-tooltip>
            </b-card-footer>
        </b-card>
        </b-form>
        </b-col>
    </b-row>
    <b-row fluid class="flex-grow-1 d-flex align-items-center justify-content-center">
        <b-col  md="6" lg="4" cols="5">
            <b-alert  v-if="datasetSaved" variant="success" show>
            Registration was successful!
            <b-button @click="$router.push('/login')" variant="primary" class="ml-2">Login</b-button>
            </b-alert>
        </b-col>
    </b-row>
</b-container>
</template>

<script>
import { apiMixin } from "../../mixins";
import { validationMixin } from "vuelidate";
import {required, minLength, maxLength, email, sameAs} from "vuelidate/lib/validators";

export default {
    name: "RegistrationForm",
    mixins: [apiMixin, validationMixin],
    data: function() {
        return {
            form: {
                userName: null,
                emailAddress: null,
                password1: null,
                password2: null
            },
            sending: false,
            datasetSaved: false
        };
    },
    validations: {
        // validators for the form
        form: {
            userName: {
                required,
                minLength: minLength(3),
                maxLength: maxLength(81)
            },
            emailAddress: {
                required,
                email
            },
            password1: {
                required,
                minLength: minLength(5)
            },
            password2: {
                required,
                sameAsFirst: sameAs('password1')
            }
        }
    },
    methods: {
        handleSubmit: function() {
            if (this.password.length > 0) {
                this.fetchAndStoreToken(this.username, this.password)
                    .then(() => {
                        //fetching and storing in store worked, redirect either to main/compare or to next url
                        this.$globalFlags["serializeCompare"] = true;
                        if (this.$route.query && this.$route.query.redirect) {
                            this.$router.push(this.$route.query.redirect);
                        } else {
                            this.$router.push("/main/compare");
                        }
                    })
                    .catch(error => {
                        // something went wrong
                        console.log(error);
                        this.showError = true;
                    });
            }
        },
        getValidationState(fieldName) {
            // assigns validation state to form fields
            const field = this.$v.form[fieldName];
            if (field) {
                return (field.$invalid && field.$dirty) ? false: null
            }
            return null;
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                if (key == 'password2') {
                    continue
                } else {
                    formData.append(key, this.form[key]);
                }
            }
            // API call including upload is made in the background
            this.registerUser(formData).then(response => {
                this.sending = false;
                this.clearForm();
                if (response) {
                    // if error happend, global error handler will eat the response
                    this.datasetSaved = true;
                }
            })
        },
        clearForm() {
            this.$v.$reset();
            this.form.userName = null;
            this.form.emailAddress = null;
            this.form.password1 = null;
            this.form.password2 = null;
        },
        validateDataset() {
            this.$v.$touch();
            console.log("triggered")
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    }
};
</script>


<style scoped>
.container {
  overflow: visible !important;
}
</style>
