<template>
    <div>
        <form
            novalidate
            class="md-layout"
            @submit.prevent="validateDataset"
            enctype="multipart/form-data"
            v-if="!datasetSaved"
        >
            <md-card md-with-hover class="halfwidth center">
                <md-card-header>
                    <div class="md-title">Register</div>
                </md-card-header>

                <md-card-content>
                    <!-- Username -->
                    <md-field :class="getValidationClass('userName')">
                        <label for="userName">Username</label>
                        <md-input
                            name="userName"
                            id="userName"
                            v-model="form.userName"
                            :disabled="sending"
                            required
                        />
                        <span class="md-error" v-if="!$v.form.userName.required"
                            >A username is required!</span
                        >
                        <span
                            class="md-error"
                            v-if="
                                !$v.form.userName.minLength ||
                                    !$v.form.userName.maxLength
                            "
                            >Username needs to be within 3 and 80
                            characters</span
                        >
                    </md-field>
                    <!-- Username -->
                    <md-field :class="getValidationClass('emailAddress')">
                        <label for="emailAddress">Email address</label>
                        <md-input
                            name="emailAddress"
                            id="emailAddress"
                            v-model="form.emailAddress"
                            :disabled="sending"
                            required
                        />
                        <span
                            class="md-error"
                            v-if="!$v.form.emailAddress.required"
                            >An email-address is required!</span
                        >
                        <span
                            class="md-error"
                            v-if="!$v.form.emailAddress.email"
                            >Not a valid format</span
                        >
                    </md-field>
                    <!-- Password 1 -->
                    <md-field :class="getValidationClass('password1')">
                        <label for="password1">Password</label>
                        <md-input
                            name="password1"
                            id="password1"
                            v-model="form.password1"
                            :disabled="sending"
                            type="password"
                            required
                        />
                        <span
                            class="md-error"
                            v-if="!$v.form.password1.required"
                            >A password is required!</span
                        >
                    </md-field>
                    <!-- Password 2 -->
                    <md-field :class="getValidationClass('password2')">
                        <label for="password2">Confirm password</label>
                        <md-input
                            name="password2"
                            id="password2"
                            v-model="form.password2"
                            :disabled="sending"
                            type="password"
                            required
                        />
                        <span
                            class="md-error"
                            v-if="!$v.form.password2.required"
                            >You need to confirm your passowrd</span
                        >
                        <span
                            class="md-error"
                            v-if="
                                !$v.form.password2.sameAsFirst &&
                                    $v.form.password2.required
                            "
                            >Passwords need to be equal</span
                        >
                    </md-field>
                </md-card-content>
                <!-- Progress bar -->
                <md-progress-bar md-mode="indeterminate" v-if="sending" />
                <!-- Buttons for user creation -->
                <md-card-actions>
                    <md-button
                        type="submit"
                        class="md-primary"
                        :disabled="sending"
                        >Create user</md-button
                    >
                    <!-- <md-button
                    class="md-primary"
                    >Create user</md-button
                ><md-tooltip md-direction="top"
                >Public registration will be available soon!</md-tooltip
                > -->
                </md-card-actions>
            </md-card>
            <!-- Submission notification -->
            <md-snackbar :md-active.sync="datasetSaved"
                >Registration was successful. Confirm your email to start
                exploring!</md-snackbar
            >
        </form>
        <md-empty-state
            md-icon="devices_other"
            md-label="Confirm your email"
            md-description="After you have confirmed your E-mail you can start exploring!"
            v-else
        >
            <md-button
                @click="$router.push('/login')"
                class="md-primary md-raised"
                >Login</md-button
            >
        </md-empty-state>
    </div>
</template>

<script>
import { apiMixin } from "../../mixins";
import { validationMixin } from "vuelidate";
import {
    required,
    minLength,
    maxLength,
    email,
    sameAs
} from "vuelidate/lib/validators";

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
                sameAsFirst: sameAs("password1")
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
        getValidationClass(fieldName) {
            // matrial validation class for form field;
            const field = this.$v.form[fieldName];

            if (field) {
                return {
                    "md-invalid": field.$invalid && field.$dirty
                };
            }
        },
        saveDataset() {
            this.sending = true; // show progress bar
            // construct form data
            var formData = new FormData();
            for (var key in this.form) {
                if (key == "password2") {
                    continue;
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
            });
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
            if (!this.$v.$invalid) {
                this.saveDataset();
            }
        }
    }
};
</script>

<style scoped>
.md-progress-bar {
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
}

.halfwidth {
    width: 20vw;
    height: 35v;
}

.center {
    margin: 0;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.red {
    color: red;
}

.floatright {
    float: right;
}
</style>
