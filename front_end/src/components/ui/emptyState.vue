<template>
    <div>
        <md-empty-state
            v-if="isDemo"
            md-icon="input"
            md-label="Explore the power of HiCognition"
            md-description=""
            class="test"
            style="width:50%; "
        >
            <p style="text-align: justify;">
                This is a Demo version of HiCognition. We deactivated the
                preprocessing features. However, you can find in the
                Documentation how to run the fully functional HiCognition in a
                few steps locally.
            </p>
            <p style="text-align: justify;">
                We have prepared a couple of datasets for you and preprocessed
                all the data to reproduce the figures from the HiCognition
                manuscript (see the table below).
            </p>
            <md-table>
                <md-table-row>
                    <md-table-head>Task</md-table-head>
                    <md-table-head>Figure</md-table-head>
                </md-table-row>
                <md-table-row>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjN9.bFeRnrclEo651eFjLhlvmYi8fSTHYncW7qB1mCX6fT8DC2RVDyIhS7HpWFa4kmEH6101pyY0oLkOgiwZ_Ossmw&sessionID=123"
                        >
                            Explore average profiles
                        </a>
                    </md-table-cell>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjN9.bFeRnrclEo651eFjLhlvmYi8fSTHYncW7qB1mCX6fT8DC2RVDyIhS7HpWFa4kmEH6101pyY0oLkOgiwZ_Ossmw&sessionID=123"
                        >
                            (Figure 2a)
                        </a>
                    </md-table-cell>
                </md-table-row>
                <md-table-row>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjR9.WdreGpseJiZQmZi_sCx7j8wSDjGl-jOYaavAK-lBGCcAXhQRonpdjbr0f9NJcbjUKBQKnfu5X1nbuy-ae4-DvQ&sessionID=124"
                        >
                            Explore average profiles and heterogeneity
                        </a>
                    </md-table-cell>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjR9.WdreGpseJiZQmZi_sCx7j8wSDjGl-jOYaavAK-lBGCcAXhQRonpdjbr0f9NJcbjUKBQKnfu5X1nbuy-ae4-DvQ&sessionID=124"
                        >
                            (Figure 2b)
                        </a>
                    </md-table-cell>
                </md-table-row>
                <md-table-row>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjV9.r6PNyssTNVXYAGTI7YL0D8L_uEirpYskD0gufbwjHMEFe7JctUUj8lrJSRoRYNMtJAIxXGNXdxHPut6wb5lPwQ&sessionID=125"
                        >
                            Explore average profiles
                        </a>
                    </md-table-cell>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjV9.r6PNyssTNVXYAGTI7YL0D8L_uEirpYskD0gufbwjHMEFe7JctUUj8lrJSRoRYNMtJAIxXGNXdxHPut6wb5lPwQ&sessionID=125"
                        >
                            (Figure 2c-f)
                        </a>
                    </md-table-cell>
                </md-table-row>
                <md-table-row>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjZ9.HpxEJpRFOYHsF9hNwBr9H-ej5qbdjyognbDUGjvaK7Kl1ZwcYX5pELJ9U03ulLonElxFnmopc3SR6g03KhR2pA&sessionID=126"
                        >
                            Exploring heterogeneity
                        </a>
                    </md-table-cell>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjZ9.HpxEJpRFOYHsF9hNwBr9H-ej5qbdjyognbDUGjvaK7Kl1ZwcYX5pELJ9U03ulLonElxFnmopc3SR6g03KhR2pA&sessionID=126"
                        >
                            (Figure 3a-b)
                        </a>
                    </md-table-cell>
                </md-table-row>
                <md-table-row>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjh9.LHAIg-Z-Td9u-7LsnCDGFVPRiKLjKODLpPbbVTjq_LaArHLO0h1hgoz16Uwum4FVp9Bzav2HA5SJO-bX0c7-Cg&sessionID=128"
                        >
                            Explore average profiles and associations
                        </a>
                    </md-table-cell>
                    <md-table-cell>
                        <a
                            href="/app/#/main/session?sessionToken=eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoxMjh9.LHAIg-Z-Td9u-7LsnCDGFVPRiKLjKODLpPbbVTjq_LaArHLO0h1hgoz16Uwum4FVp9Bzav2HA5SJO-bX0c7-Cg&sessionID=128"
                        >
                            (Figure 3c-d)
                        </a>
                    </md-table-cell>
                </md-table-row>
            </md-table>
            <p style="text-align: justify;">
                If you want to explore datasets on your own, the region-sets:
                <i>'SMC3 Stag1 only'</i>, <i>SMC3 Stag2 only'</i>, or
                <i>'pc_genes_forward_tss'</i> are good places to start.
            </p>
            <!-- md-icon="../../static/logo.svg" -->
            <!-- <img v-bind:src="'../../static/logo.svg'"> -->
        </md-empty-state>
    </div>
</template>

<script>
export default {
    name: "EmptyStateBasic",
    data: function() {
        return {
            isDemo: process.env.SHOWCASE
        };
    }
};
</script>

<style scoped>
.md-empty-state {
    max-width: 5000px !important;
    /* color: red; */
}
.md-table-row {
    text-align: justify;
    /* color: red; */
}
</style>
