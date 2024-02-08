<script setup lang="ts">
import { ref } from 'vue';
import CArmDial from './CArmDial.vue';

const percent = ref(0.5);
</script>

<template>
  <div class="controls">
    <c-arm-dial v-model="percent" :size="200"></c-arm-dial>
    <div>{{ (percent * 100).toFixed(0) }}%</div>
  </div>
</template>

<style type="text/css" scoped>
.controls {
  display: flex;
  flex-flow: column;
  align-items: center;
}
</style>
