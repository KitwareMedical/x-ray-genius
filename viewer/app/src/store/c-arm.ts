import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

const useCArmStore = defineStore('cArm', () => {
  // [0.0, 1.0]
  const rotation = ref(0.5);
  // [0.0, 1.0]
  const xTranslation = ref(0.5);
  // [0.0, 1.0]
  const zTranslation = ref(0.5);
  // [0.0, 1.0]
  const tilt = ref(0.5);

  function setRotation(value: number) {
    rotation.value = value;
  }

  function setXTranslation(value: number) {
    xTranslation.value = value;
  }

  function setZTranslation(value: number) {
    zTranslation.value = value;
  }

  function setTilt(value: number) {
    tilt.value = value;
  }

  return {
    rotation,
    setRotation,
    xTranslation,
    zTranslation,
    setXTranslation,
    setZTranslation,
    tilt,
    setTilt,
  };
});

export default useCArmStore;
