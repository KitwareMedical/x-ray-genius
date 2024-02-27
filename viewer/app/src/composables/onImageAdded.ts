import { useImageStore } from '@/src/store/datasets-images';
import { storeToRefs } from 'pinia';
import { watch, watchEffect } from 'vue';

export function onImageAdded(callback: (added: string) => void) {
  const { dataIndex } = storeToRefs(useImageStore());
  return watch(
    dataIndex,
    (newIndex, oldIndex) => {
      const added = Object.keys(oldIndex).filter((id) => id in newIndex);
      added.forEach((id) => {
        callback(id);
      });
    },
    { deep: true }
  );
}
