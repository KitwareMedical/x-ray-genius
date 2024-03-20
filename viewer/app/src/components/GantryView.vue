<script setup lang="ts">
import { ref, toRefs, watchPostEffect, nextTick } from 'vue';
import { watchImmediate } from '@vueuse/core';
import type { LPSAxisDir } from '@/src/types/lps';
import type { VtkViewApi } from '@/src/types/vtk-types';
import { useCurrentImage } from '@/src/composables/useCurrentImage';
import VtkVolumeView from '@/src/components/vtk/VtkVolumeView.vue';
import VtkBaseVolumeRepresentation from '@/src/components/vtk/VtkBaseVolumeRepresentation.vue';
import useVolumeColoringStore from '@/src/store/view-configs/volume-coloring';
import CArmModel from './CArmModel.vue';
import { useViewAnimationListener } from '@/src/composables/useViewAnimationListener';

interface Props {
  id: string;
  type: string;
  viewDirection: LPSAxisDir;
  viewUp: LPSAxisDir;
}

const props = defineProps<Props>();
const { id: viewId, type: viewType, viewDirection, viewUp } = toRefs(props);

const vtkView = ref<VtkViewApi>();
const volumeColoringStore = useVolumeColoringStore();
const { currentImageID } = useCurrentImage();

useViewAnimationListener(vtkView, viewId, viewType);

// watchPost so we can initialize the default volume coloring config
watchPostEffect(() => {
  const imageId = currentImageID.value;
  if (!imageId) return;

  // disable CVR
  volumeColoringStore.updateCVRParameters(viewId.value, imageId, {
    enabled: false,
  });
});

function resetCamera() {
  if (!vtkView.value) return;
  // reset to face image
  vtkView.value.resetCamera();
  // reset to include gantry
  vtkView.value.renderer.resetCamera();
  vtkView.value.requestRender();
}

// hack to call our reset camera after VtkVolumeView's resetCamera
watchImmediate([viewId, currentImageID], () => {
  nextTick(resetCamera);
});
</script>

<template>
  <div class="vtk-container-wrapper" tabindex="0">
    <div class="vtk-gutter">
      <v-btn dark icon size="medium" variant="text" @click="resetCamera">
        <v-icon size="medium" class="py-1">mdi-camera-flip-outline</v-icon>
        <v-tooltip
          location="right"
          activator="parent"
          transition="slide-x-transition"
        >
          Reset Camera
        </v-tooltip>
      </v-btn>
    </div>
    <div class="vtk-container">
      <div class="vtk-sub-container">
        <vtk-volume-view
          class="vtk-view"
          ref="vtkView"
          :view-id="id"
          :image-id="currentImageID"
          :view-direction="viewDirection"
          :view-up="viewUp"
          disable-auto-reset-camera
        >
          <vtk-base-volume-representation
            :view-id="id"
            :image-id="currentImageID"
          ></vtk-base-volume-representation>
          <c-arm-model :image-id="currentImageID"></c-arm-model>
          <slot></slot>
        </vtk-volume-view>
      </div>
    </div>
  </div>
</template>

<style scoped src="@/src/components/styles/vtk-view.css"></style>
