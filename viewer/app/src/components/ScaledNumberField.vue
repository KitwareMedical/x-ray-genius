<script setup lang="ts">
import { ref, toRef } from 'vue';
import { syncRef } from '@vueuse/core';

interface Props {
  /**
   * The scale factor, going from user entry to the v-model.
   */
  scaleFactor: number;
}

const props = defineProps<Props>();
const scaleFactor = toRef(props, 'scaleFactor');
const modelValue = defineModel<number>({ required: true });
const internalValue = ref(modelValue.value);

syncRef(modelValue, internalValue, {
  transform: {
    ltr: (left) => left / scaleFactor.value,
    rtl: (right) => right * scaleFactor.value,
  },
});
</script>

<template>
  <v-text-field type="number" v-model="internalValue"></v-text-field>
</template>
