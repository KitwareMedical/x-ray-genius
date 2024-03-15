<script setup lang="ts">
import VolViewApp from '@/src/components/App.vue';
import { useViewStore } from '@/src/store/views';
import { Layouts, DefaultLayoutName } from '../config';

const viewStore = useViewStore();
viewStore.setLayout(Layouts[DefaultLayoutName]);
</script>

<template>
  <VolViewApp />
</template>
