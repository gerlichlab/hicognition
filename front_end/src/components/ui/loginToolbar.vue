<template>
  <div>
    <b-navbar-brand class="d-flex w-100 justify-content-between">
      <span>HiCognition {{ appversion }}</span>
    </b-navbar-brand>
  </div>
</template>

<script>
export default {
  name: "loginToolbar",
  data: function () {
    return {
      appversion: process.env.VERSION,
    };
  },
};
</script>