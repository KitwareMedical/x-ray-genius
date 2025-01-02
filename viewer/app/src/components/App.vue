<script setup lang="ts">
import VolViewApp from '@/src/components/App.vue';
import { useViewStore } from '@/src/store/views';
import { Layouts, DefaultLayoutName } from '../config';
import { onImageAdded } from '../composables/onImageAdded';
import { useImageStore } from '@/src/store/datasets-images';
import { mat3, vec3 } from 'gl-matrix';
import { ImageMetadata } from '@/src/types/image';
import { Vector3 } from '@kitware/vtk.js/types';

const viewStore = useViewStore();
viewStore.setLayout(Layouts[DefaultLayoutName]);

/**
 * Gets the basis vector flip factors when compared to LPS.
 */
function getFlipFactors(metadata: ImageMetadata) {
  const { orientation, lpsOrientation } = metadata;
  const { Left, Posterior, Superior, Coronal, Sagittal, Axial } =
    lpsOrientation;
  const sVec = orientation.slice(Sagittal * 3, Sagittal * 3 + 3) as vec3;
  const cVec = orientation.slice(Coronal * 3, Coronal * 3 + 3) as vec3;
  const aVec = orientation.slice(Axial * 3, Axial * 3 + 3) as vec3;
  return [
    Math.sign(vec3.dot(sVec, Left)),
    Math.sign(vec3.dot(cVec, Posterior)),
    Math.sign(vec3.dot(aVec, Superior)),
  ] as Vector3;
}

// re-orient image to be supine and centered at the origin
onImageAdded((id) => {
  const store = useImageStore();
  const image = store.dataIndex[id];
  const metadata = store.metadata[id];

  const dims = image.getDimensions();
  const spacing = image.getSpacing();
  const flipFactors = getFlipFactors(metadata);
  image.setOrigin(
    dims.map((d, i) => (-flipFactors[i] * (d * spacing[i])) / 2) as Vector3
  );

  const { lpsOrientation } = metadata;
  const transform = [
    ...lpsOrientation.Left,
    ...lpsOrientation.Posterior,
    ...lpsOrientation.Superior,
  ] as mat3;
  mat3.invert(transform, transform);

  const orientation = mat3.create();
  mat3.mul(orientation, transform, image.getDirection());
  image.setDirection(orientation);

  image.computeTransforms();
  store.updateData(id, image);
});
</script>

<template>
  <VolViewApp />
</template>
