<template>
  <div class="vtk-container-wrapper vtk-three-container">
    <div class="vtk-container">
      <div class="vtk-sub-container">
        <div
          class="vtk-view"
          ref="vtkContainerRef"
          data-testid="vtk-view vtk-three-view"
        />
      </div>
      <transition name="loading">
        <div v-if="isImageLoading" class="overlay-no-events loading">
          <div>Loading the image</div>
          <div>
            <v-progress-circular indeterminate color="blue" />
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onBeforeUnmount,
  onMounted,
  PropType,
  ref,
  toRefs,
  watch,
  watchEffect,
} from 'vue';

import vtkVolumeRepresentationProxy from '@kitware/vtk.js/Proxy/Representations/VolumeRepresentationProxy';
import { useProxyRepresentation } from '@/src/composables/useProxyRepresentations';
import { useColoringEffect } from '@/src/composables/useColoringEffect';
import { useResizeObserver } from '@/src/composables/useResizeObserver';
import { useCurrentImage } from '@/src/composables/useCurrentImage';
import vtkLPSView3DProxy from '@/src/vtk/LPSView3DProxy';
import { LPSAxisDir } from '@/src/types/lps';
import { useViewProxy } from '@/src/composables/useViewProxy';
import { ViewProxyType } from '@/src/core/proxies';
import useVolumeColoringStore from '@/src/store/view-configs/volume-coloring';
import { useCArmModel } from '../composables/useCArmModel';
import { useCArmCamera } from '../composables/useCArmCamera';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const volumeColoringStore = useVolumeColoringStore();

    const { id: viewID } = toRefs(props);

    const vtkContainerRef = ref<HTMLElement>();

    // --- computed vars --- //

    const { currentImageID: curImageID, isImageLoading } = useCurrentImage();

    // --- view proxy setup --- //

    const { viewProxy } = useViewProxy<vtkLPSView3DProxy>(
      viewID,
      ViewProxyType.XRay
    );

    onMounted(() => {
      viewProxy.value.setOrientationAxesVisibility(true);
      viewProxy.value.setOrientationAxesType('cube');
      viewProxy.value.setBackground([0, 0, 0, 0]);
      viewProxy.value.setContainer(vtkContainerRef.value ?? null);
    });

    onBeforeUnmount(() => {
      viewProxy.value.setContainer(null);
    });

    useResizeObserver(vtkContainerRef, () => viewProxy.value.resize());

    // --- scene setup --- //

    const { representation: baseImageRep } =
      useProxyRepresentation<vtkVolumeRepresentationProxy>(curImageID, viewID);

    // --- coloring setup --- //

    const volumeColorConfig = computed(() =>
      volumeColoringStore.getConfig(viewID.value, curImageID.value)
    );

    // --- coloring --- //

    watchEffect(() => {
      if (!curImageID.value) return;
      volumeColoringStore.updateColorBy(viewID.value, curImageID.value, {
        arrayName: String(Math.random()),
      });
      volumeColoringStore.setColorPreset(
        viewID.value,
        curImageID.value,
        'CT-X-ray'
      );
    });

    useColoringEffect(volumeColorConfig, baseImageRep, viewProxy);

    useCArmCamera(viewProxy, curImageID);

    // --- template vars --- //

    return {
      vtkContainerRef,
      viewID,
      isImageLoading,
    };
  },
});
</script>

<style scoped src="@/src/components/styles/vtk-view.css"></style>
<style scoped src="@/src/components/styles/utils.css"></style>

<style scoped>
.vtk-three-container {
  background-color: black;
  grid-template-columns: auto;
}
</style>
