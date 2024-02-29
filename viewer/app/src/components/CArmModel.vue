<script setup lang="ts">
import { Maybe } from '@/src/types';
import { useCArmModel } from '../composables/useCArmModel';
import { inject } from 'vue';
import { VtkViewContext } from '@/src/components/vtk/context';
import { toRef } from 'vue';

interface Props {
  imageId: Maybe<string>;
}

const props = defineProps<Props>();

const view = inject(VtkViewContext);
if (!view) throw new Error('Not in a vtk view context!');

useCArmModel(view, toRef(props, 'imageId'));
</script>

<template><slot></slot></template>
