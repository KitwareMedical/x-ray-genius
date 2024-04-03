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
import { useViewAnimationListener } from '@/src/composables/useViewAnimationListener';
import { usePointerDelta } from '../composables/usePointerDelta';
import { watchEffect } from 'vue';
import { vtkFieldRef } from '@/src/core/vtk/vtkFieldRef';
import { computed } from 'vue';
import { watch } from 'vue';
import { whenever } from '@vueuse/core';
import { Vector2 } from '@kitware/vtk.js/types';
import { OpacityPoints } from '@/src/types/views';
import useViewAnimationStore from '@/src/store/view-animation';

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

useViewAnimationListener(view, viewId, 'XRay');

const volumeColoringStore = useVolumeColoringStore();
const { currentImageID } = useCurrentImage();

// watchPost so we can initialize the default volume coloring config
watch(
  [currentImageID, viewId],
  () => {
    const imageId = currentImageID.value;
    if (!imageId) return;

    // disable CVR
    volumeColoringStore.updateCVRParameters(viewId.value, imageId, {
      enabled: false,
    });

    // set x-ray preset
    volumeColoringStore.setColorPreset(viewId.value, imageId, 'CT-X-ray');
  },
  { flush: 'post' }
);

useCArmCamera(view, currentImageID);

// mouse dragging behavior

function usePseudoWindowLevel() {
  const viewAnimationStore = useViewAnimationStore();
  const animationRequestor = Symbol();
  const viewSize = vtkFieldRef(view.renderWindowView, 'size');
  const container = vtkFieldRef(view.renderWindowView, 'container');

  const { dx, dy, dragging } = usePointerDelta(container);

  const normDx = computed(() => dx.value / viewSize.value[0]);
  const normDy = computed(() => dy.value / viewSize.value[1]);

  const opacityConfig = computed(
    () =>
      volumeColoringStore.getConfig(viewId.value, currentImageID.value)
        ?.opacityFunction as OpacityPoints | undefined
  );

  const initialShift = ref(0);
  const initialShiftAlpha = ref(0);
  const newShift = computed(() => initialShift.value + 4 * normDx.value);
  const newShiftAlpha = computed(
    () => initialShiftAlpha.value + 4 * normDy.value
  );

  whenever(dragging, () => {
    if (!opacityConfig.value) return;
    initialShift.value = opacityConfig.value.shift;
    initialShiftAlpha.value = opacityConfig.value.shiftAlpha;
    viewAnimationStore.requestAnimation(animationRequestor, {
      byViewIds: [viewId.value],
    });
  });

  whenever(
    computed(() => !dragging.value),
    () => {
      viewAnimationStore.cancelAnimation(animationRequestor);
    }
  );

  watch([currentImageID, viewId, newShift, dragging], () => {
    const imageId = currentImageID.value;
    if (!dragging.value || !imageId) return;
    volumeColoringStore.updateOpacityFunction(viewId.value, imageId, {
      shift: newShift.value,
      shiftAlpha: newShiftAlpha.value,
    });
    view.requestRender();
  });
}

usePseudoWindowLevel();

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
