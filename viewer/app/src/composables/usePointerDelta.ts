import { Maybe } from '@/src/types';
import { useEventListener, usePointer } from '@vueuse/core';
import { MaybeRef, computed, ref, watchEffect } from 'vue';

export function usePointerDelta(element: MaybeRef<Maybe<HTMLElement>>) {
  const sx = ref(0);
  const sy = ref(0);
  const dragging = ref(false);

  const { x: pointerX, y: pointerY } = usePointer({ target: element });

  const dx = computed(() => sx.value - pointerX.value);
  const dy = computed(() => sy.value - pointerY.value);

  useEventListener(element, 'pointerdown', () => {
    dragging.value = true;
    sx.value = pointerX.value;
    sy.value = pointerY.value;
  });
  useEventListener(window, 'pointerup', () => {
    dragging.value = false;
  });
  useEventListener(window, 'pointercancel', () => {
    dragging.value = false;
  });

  return { dragging, dx, dy };
}
