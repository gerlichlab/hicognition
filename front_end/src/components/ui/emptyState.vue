<template>
  <div>
    <md-empty-state
      v-if=(showcase_bool)
      md-icon="devices_other"
      md-label="Explore the power of HiCognition"
      md-description="Creating project, you'll be able to upload your design and collaborate with people.">
      <md-button class="md-primary md-raised">Create {{showcase_bool}} first project </md-button>
    </md-empty-state>

  </div>
</template>

<script>
  export default {
    name: 'EmptyStateBasic',
    data: function() {
        return {
            showcase_bool: process.env.SHOWCASE
        };
    },
  }
</script>