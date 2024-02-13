<template>
  <div class="vtk-container-wrapper vtk-three-container">
    <div class="vtk-container" :class="active ? 'active' : ''">
      <div class="vtk-sub-container">
        <div
          class="vtk-view"
          ref="vtkContainerRef"
          data-testid="vtk-view vtk-three-view"
        />
      </div>
      <view-overlay-grid class="overlay-no-events view-annotations">
        <template v-slot:top-left>
          <div class="annotation-cell">
            <v-btn
              class="pointer-events-all"
              dark
              icon
              size="medium"
              variant="text"
              @click="resetCamera"
            >
              <v-icon size="medium" class="py-1">
                mdi-camera-flip-outline
              </v-icon>
              <v-tooltip
                location="right"
                activator="parent"
                transition="slide-x-transition"
              >
                Reset Camera
              </v-tooltip>
            </v-btn>
          </div>
        </template>
      </view-overlay-grid>
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
  nextTick,
} from 'vue';
import { vec3 } from 'gl-matrix';

import vtkVolumeRepresentationProxy from '@kitware/vtk.js/Proxy/Representations/VolumeRepresentationProxy';
import { useProxyRepresentation } from '@/src/composables/useProxyRepresentations';
import ViewOverlayGrid from '@/src/components/ViewOverlayGrid.vue';
import { useColoringEffect } from '@/src/composables/useColoringEffect';
import { useResizeObserver } from '@/src/composables/useResizeObserver';
import { useCurrentImage } from '@/src/composables/useCurrentImage';
import { useCameraOrientation } from '@/src/composables/useCameraOrientation';
import vtkLPSView3DProxy from '@/src/vtk/LPSView3DProxy';
import { usePersistCameraConfig } from '@/src/composables/usePersistCameraConfig';
import { LPSAxisDir } from '@/src/types/lps';
import { useViewProxy } from '@/src/composables/useViewProxy';
import { ViewProxyType } from '@/src/core/proxies';
import useVolumeColoringStore from '@/src/store/view-configs/volume-coloring';
import useViewCameraStore from '@/src/store/view-configs/camera';
import { useResetViewsEvents } from '@/src/components/tools/ResetViews.vue';
import { useCArm } from '../composables/useCArm';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
    viewDirection: {
      type: String as PropType<LPSAxisDir>,
      required: true,
    },
    viewUp: {
      type: String as PropType<LPSAxisDir>,
      required: true,
    },
  },
  components: {
    ViewOverlayGrid,
  },
  setup(props) {
    const volumeColoringStore = useVolumeColoringStore();
    const viewCameraStore = useViewCameraStore();

    const { id: viewID, viewDirection, viewUp } = toRefs(props);

    const vtkContainerRef = ref<HTMLElement>();

    // --- computed vars --- //

    const {
      currentImageID: curImageID,
      currentImageMetadata: curImageMetadata,
      currentImageData,
      isImageLoading,
    } = useCurrentImage();

    // --- view proxy setup --- //

    const { viewProxy } = useViewProxy<vtkLPSView3DProxy>(
      viewID,
      ViewProxyType.Volume
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

    useCArm(viewProxy, curImageID, 200);

    // --- picking --- //

    // disables picking for crop control and more
    watch(
      baseImageRep,
      (rep) => {
        if (rep) {
          rep.getVolumes().forEach((volume) => volume.setPickable(false));
        }
      },
      { immediate: true }
    );

    // --- camera setup --- //

    const { cameraUpVec, cameraDirVec } = useCameraOrientation(
      viewDirection,
      viewUp,
      curImageMetadata
    );

    const resetCamera = () => {
      const bounds = curImageMetadata.value.worldBounds;
      const center = [
        (bounds[0] + bounds[1]) / 2,
        (bounds[2] + bounds[3]) / 2,
        (bounds[4] + bounds[5]) / 2,
      ] as vec3;

      viewProxy.value.updateCamera(
        cameraDirVec.value,
        cameraUpVec.value,
        center
      );
      viewProxy.value.resetCamera();
      viewProxy.value.renderLater();
    };

    watch(
      [baseImageRep, cameraDirVec, cameraUpVec],
      () => {
        const cameraConfig = viewCameraStore.getConfig(
          viewID.value,
          curImageID.value
        );

        // We don't want to reset the camera if we have a config we are restoring
        if (!cameraConfig) {
          // nextTick ensures resetCamera gets called after
          // useSceneBuilder refreshes the scene.
          nextTick(resetCamera);
        }
      },
      {
        immediate: true,
      }
    );

    const { restoreCameraConfig } = usePersistCameraConfig(
      viewID,
      curImageID,
      viewProxy,
      'position',
      'focalPoint',
      'directionOfProjection',
      'viewUp'
    );

    watch(curImageID, () => {
      // See if we have a camera configuration to restore
      const cameraConfig = viewCameraStore.getConfig(
        viewID.value,
        curImageID.value
      );

      if (cameraConfig) {
        restoreCameraConfig(cameraConfig);

        viewProxy.value.getRenderer().resetCameraClippingRange();
        viewProxy.value.renderLater();
      }
    });

    // --- coloring setup --- //

    const volumeColorConfig = computed(() =>
      volumeColoringStore.getConfig(viewID.value, curImageID.value)
    );

    watch(
      [viewID, curImageID],
      () => {
        if (
          curImageID.value &&
          currentImageData.value &&
          !volumeColorConfig.value
        ) {
          volumeColoringStore.resetToDefaultColoring(
            viewID.value,
            curImageID.value,
            currentImageData.value
          );
        }
      },
      { immediate: true }
    );

    // --- coloring --- //

    useColoringEffect(volumeColorConfig, baseImageRep, viewProxy);

    // --- Listen to ResetViews event --- //
    const events = useResetViewsEvents();
    events.onClick(() => resetCamera());

    // --- template vars --- //

    return {
      vtkContainerRef,
      viewID,
      active: false,
      isImageLoading,
      resetCamera,
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
