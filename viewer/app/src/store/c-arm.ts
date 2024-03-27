import { Vector3 } from '@kitware/vtk.js/types';
import { defineStore } from 'pinia';
import { ref, MaybeRef, computed } from 'vue';
import { Maybe } from '@/src/types';
import { useImage } from '@/src/composables/useCurrentImage';

const INCHES_TO_MM = 25.4;
const DEFAULT_STANDARD_DEVIATION = 20; // mm
// 9" I.I. Standard C-arm from the OEC Elite doc
const DEFAULT_SOURCE_TO_DETECTOR_DISTANCE = 1000; // mm
const DEFAULT_DETECTOR_DIAMETER = 9 /* in */ * INCHES_TO_MM; // mm
const DEFAULT_NUMBER_OF_SAMPLES = 100;
const DEFAULT_KAPPA_STD_DEV = 5; // deg

const useCArmStore = defineStore('cArm', () => {
  // [0.0, 1.0] -> 2*PI. aka alpha
  const rotation = ref(0.5);
  const rotationKappaStdDev = ref(DEFAULT_KAPPA_STD_DEV);
  // [-0.5, 0.5] -> dimensions. [0, 0, 0] is the center.
  const translation = ref<Vector3>([0, 0, 0]);
  // [0.0, 1.0] -> 2*PI. aka beta
  const tilt = ref(0.5);
  const tiltKappaStdDev = ref(DEFAULT_KAPPA_STD_DEV);
  // mm
  const sourceToDetectorDistance = ref(DEFAULT_SOURCE_TO_DETECTOR_DISTANCE);
  // mm
  const detectorDiameter = ref(DEFAULT_DETECTOR_DIAMETER);

  const numberOfSamples = ref(DEFAULT_NUMBER_OF_SAMPLES);

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

  function setRotationKappaStdDev(value: number) {
    rotationKappaStdDev.value = value;
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

  function setTiltKappaStdDev(value: number) {
    tiltKappaStdDev.value = value;
  }

  function setNumberOfSamples(value: number) {
    numberOfSamples.value = value;
  }

  return {
    rotation,
    setRotation,
    rotationKappaStdDev,
    setRotationKappaStdDev,
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
    tiltKappaStdDev,
    setTiltKappaStdDev,
    randomizeTilt,
    sourceToDetectorDistance,
    setSourceToDetectorDistance,
    detectorDiameter,
    setDetectorDiameter,
    numberOfSamples,
    setNumberOfSamples,
  };
});

export function useCArmPhysicalParameters(imageId: MaybeRef<Maybe<string>>) {
  const cArmStore = useCArmStore();
  const { metadata } = useImage(imageId);
  const dimensions = computed(() => metadata.value.dimensions);
  const spacing = computed(() => metadata.value.spacing);
  const armTranslation = computed(() => {
    return cArmStore.translation.map(
      (v, i) =>
        v *
        Math.max(
          dimensions.value[i] * spacing.value[i],
          cArmStore.sourceToDetectorDistance
        )
    ) as Vector3;
  });

  // rotation angle around Z
  const armRotation = computed(() => {
    // map [0,1] to [-0.5,0.5] * range
    return (cArmStore.rotation - 0.5) * 2 * Math.PI;
  });
  const armRotationDeg = computed(() => (armRotation.value * 180) / Math.PI);
  // tilt angle around X
  const armTilt = computed(() => {
    // map [0,1] to [-0.5,0.5] * range
    return (cArmStore.tilt - 0.5) * 2 * Math.PI;
  });
  const armTiltDeg = computed(() => (armTilt.value * 180) / Math.PI);

  return {
    armTranslation,
    armRotation,
    armRotationDeg,
    armTilt,
    armTiltDeg,
  };
}

export default useCArmStore;
