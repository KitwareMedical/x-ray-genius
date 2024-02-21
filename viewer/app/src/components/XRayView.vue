<script setup lang="ts">
import { ref, toRefs, watchPostEffect } from 'vue';
import type { VtkViewApi } from '@/src/types/vtk-types';
import { useCurrentImage } from '@/src/composables/useCurrentImage';
import VtkBaseVolumeRepresentation from '@/src/components/vtk/VtkBaseVolumeRepresentation.vue';
import useVolumeColoringStore from '@/src/store/view-configs/volume-coloring';
import { effectScope } from 'vue';
import { useVtkView } from '@/src/core/vtk/useVtkView';
import { onUnmounted } from 'vue';
import { toRaw } from 'vue';
import { provide } from 'vue';
import { VtkViewContext } from '@/src/components/vtk/context';
import { useCArmCamera } from '../composables/useCArmCamera';

interface Props {
  id: string;
  type: string;
}

const props = defineProps<Props>();
const { id: viewId } = toRefs(props);

const vtkContainerRef = ref<HTMLElement>();

// use a detached scope so that actors can be removed from
// the renderer before the renderer is deleted.
const scope = effectScope(true);
const view = scope.run(() => useVtkView(vtkContainerRef))!;
onUnmounted(() => {
  scope.stop();
});

view.renderer.setBackground(0, 0, 0);

const volumeColoringStore = useVolumeColoringStore();
const { currentImageID } = useCurrentImage();

// watchPost so we can initialize the default volume coloring config
watchPostEffect(() => {
  const imageId = currentImageID.value;
  if (!imageId) return;

  // disable CVR
  volumeColoringStore.updateCVRParameters(viewId.value, imageId, {
    enabled: false,
  });

  // set x-ray preset
  volumeColoringStore.setColorPreset(viewId.value, imageId, 'CT-X-ray');
});

useCArmCamera(view, currentImageID);

// exposed API
const api: VtkViewApi = toRaw({
  ...view,
  // no-op
  resetCamera: () => {},
});

defineExpose(api);
provide(VtkViewContext, api);
</script>

<template>
  <div class="vtk-container">
    <div class="vtk-sub-container">
      <div ref="vtkContainerRef" class="vtk-view">
        <vtk-base-volume-representation
          :view-id="id"
          :view-type="type"
          :image-id="currentImageID"
        ></vtk-base-volume-representation>
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<style scoped src="@/src/components/styles/vtk-view.css"></style>
