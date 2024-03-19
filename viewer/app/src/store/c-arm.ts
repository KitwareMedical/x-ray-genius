import { Vector3 } from '@kitware/vtk.js/types';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { CArmParameters } from '../api';

const DEFAULT_STANDARD_DEVIATION = 200; // mm

const useCArmStore = defineStore('cArm', () => {
  // [0.0, 1.0] -> 2*PI. aka alpha
  const rotation = ref(0.5);
  const rotationKappa = ref(100);
  // [-0.5, 0.5] -> dimensions. [0, 0, 0] is the center.
  const translation = ref<Vector3>([0, 0, 0]);
  // [0.0, 1.0] -> 2*PI. aka beta
  const tilt = ref(0.5);
  const tiltKappa = ref(100);
  // mm
  const sourceToDetectorDistance = ref(1000);
  // mm
  const detectorDiameter = ref(304);

  const numberOfSamples = ref(100);

  const randomizeRotation = ref(false);
  const randomizeTilt = ref(false);
  const randomizeX = ref(false);
  const randomizeY = ref(false);
  const randomizeZ = ref(false);
  const randStdDevX = ref(DEFAULT_STANDARD_DEVIATION);
  const randStdDevY = ref(DEFAULT_STANDARD_DEVIATION);
  const randStdDevZ = ref(DEFAULT_STANDARD_DEVIATION);

  function setSourceToDetectorDistance(value: number) {
    sourceToDetectorDistance.value = value;
  }

  function setDetectorDiameter(value: number) {
    detectorDiameter.value = value;
  }

  function setRotation(value: number) {
    rotation.value = value;
  }

  function setRotationKappa(value: number) {
    rotationKappa.value = value;
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

  function setTiltKappa(value: number) {
    tiltKappa.value = value;
  }

  function setNumberOfSamples(value: number) {
    numberOfSamples.value = value;
  }

  return {
    rotation,
    setRotation,
    rotationKappa,
    setRotationKappa,
    randomizeRotation,
    translation,
    setXTranslation,
    setYTranslation,
    setZTranslation,
    randomizeX,
    randomizeY,
    randomizeZ,
    randStdDevX,
    randStdDevY,
    randStdDevZ,
    tilt,
    setTilt,
    tiltKappa,
    setTiltKappa,
    randomizeTilt,
    sourceToDetectorDistance,
    setSourceToDetectorDistance,
    detectorDiameter,
    setDetectorDiameter,
    numberOfSamples,
    setNumberOfSamples,
  };
});

export default useCArmStore;
