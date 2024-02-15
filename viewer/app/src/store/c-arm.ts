import { Vector3 } from '@kitware/vtk.js/types';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

const useCArmStore = defineStore('cArm', () => {
  // [0.0, 1.0] -> 2*PI. aka alpha
  const rotation = ref(0.5);
  // [0.0, 1.0] -> dimensions
  const translation = ref<Vector3>([0.5, 0.5, 0.5]);
  // [0.0, 1.0] -> 2*PI. aka beta
  const tilt = ref(0.5);
  // mm
  const sourceToDetectorDistance = ref(1000);
  // mm
  const detectorDiameter = ref(304);

  function setSourceToDetectorDistance(value: number) {
    sourceToDetectorDistance.value = value;
  }

  function setDetectorDiameter(value: number) {
    detectorDiameter.value = value;
  }

  function setRotation(value: number) {
    rotation.value = value;
  }

  function setXTranslation(x: number) {
    const [, y, z] = translation.value;
    translation.value = [x, y, z];
  }

  function setYTranslation(y: number) {
    const [x, , z] = translation.value;
    translation.value = [x, y, z];
  }

  function setZTranslation(z: number) {
    const [x, y] = translation.value;
    translation.value = [x, y, z];
  }

  function setTilt(value: number) {
    tilt.value = value;
  }

  return {
    rotation,
    setRotation,
    translation,
    setXTranslation,
    setYTranslation,
    setZTranslation,
    tilt,
    setTilt,
    sourceToDetectorDistance,
    setSourceToDetectorDistance,
    detectorDiameter,
    setDetectorDiameter,
  };
});

export default useCArmStore;
