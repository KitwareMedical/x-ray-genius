<script setup lang="ts">
import CArmDial from './CArmDial.vue';
import useCArmStore from '../store/c-arm';
import { computed } from 'vue';
import { onImageAdded } from '../composables/onImageAdded';
import { useImageStore } from '@/src/store/datasets-images';
import { mat3 } from 'gl-matrix';
import vtkBoundingBox from '@kitware/vtk.js/Common/DataModel/BoundingBox';
import { Vector3 } from '@kitware/vtk.js/types';

const imageStore = useImageStore();

onImageAdded((id) => {
  const image = imageStore.dataIndex[id];
  const { lpsOrientation } = imageStore.metadata['id'];
  const { Sagittal, Coronal, Axial } = lpsOrientation;
  const newDirection = mat3.create();
  [Sagittal, Coronal, Axial].forEach((column, xyzIndex) => {
    // column major
    newDirection[column * 3 + 0] = xyzIndex === 0 ? 1 : 0;
    newDirection[column * 3 + 1] = xyzIndex === 1 ? 1 : 0;
    newDirection[column * 3 + 2] = xyzIndex === 2 ? 1 : 0;
  });

  const bounds = image.getBounds();
  const center = vtkBoundingBox.getCenter(bounds);

  image.setDirection(newDirection);
  image.setOrigin(center.map((v) => -v) as Vector3);
  image.computeTransforms();

  imageStore.updateData(id, image);
});

const store = useCArmStore();
const tilt = computed({
  get: () => store.tilt,
  set: (v) => {
    store.setTilt(v);
  },
});
const xTranslation = computed({
  get: () => store.xTranslation,
  set: (v) => {
    store.setXTranslation(v);
  },
});
const zTranslation = computed({
  get: () => store.zTranslation,
  set: (v) => {
    store.setZTranslation(v);
  },
});
const dialPosition = computed({
  get: () => store.rotation,
  set: (v) => {
    store.setRotation(v);
  },
});
</script>

<template>
  <div class="controls">
    <c-arm-dial v-model="dialPosition" :size="200"></c-arm-dial>
    <div>{{ (dialPosition * 100).toFixed(0) }}%</div>
    <v-slider
      v-model="xTranslation"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      label="X Translation"
    ></v-slider>
    <v-slider
      v-model="zTranslation"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      label="Z Translation"
    ></v-slider>
    <v-slider
      v-model="tilt"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      label="Tilt"
    ></v-slider>
  </div>
</template>

<style type="text/css" scoped>
.controls {
  display: flex;
  flex-flow: column;
  align-items: center;
}
</style>
