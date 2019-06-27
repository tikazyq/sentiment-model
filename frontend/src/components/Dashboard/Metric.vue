<template>
  <div class="metric">
  </div>
</template>

<script>
export default {
  name: 'Metric',
  props: {
    title: {
      type: String,
      default: ''
    },
    value: {
      type: Number,
      default: undefined
    },
    change: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>

</style>
