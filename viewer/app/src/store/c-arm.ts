import { Vector3 } from '@kitware/vtk.js/types';
import { defineStore, storeToRefs } from 'pinia';
import { ref, MaybeRef, computed } from 'vue';
import { Maybe } from '@/src/types';
import { useImage } from '@/src/composables/useCurrentImage';

const DEG_TO_RAD = Math.PI / 180;
const INCHES_TO_MM = 25.4;
const DEFAULT_STANDARD_DEVIATION = 20; // mm
// 9" I.I. Standard C-arm from the OEC Elite doc
const DEFAULT_SOURCE_TO_DETECTOR_DISTANCE = 1000; // mm
const DEFAULT_DETECTOR_DIAMETER = 9 /* in */ * INCHES_TO_MM; // mm
const DEFAULT_NUMBER_OF_SAMPLES = 100;
const DEFAULT_KAPPA_STD_DEV = 5; // deg

const useCArmStore = defineStore('cArm', () => {
  // [-180, 180] deg
  const rotation = ref(0);
  const rotationKappaStdDev = ref(DEFAULT_KAPPA_STD_DEV);
  // LPS translation in mm. [0, 0, 0] is the center of the volume.
  const translation = ref<Vector3>([0, 0, 0]);
  // [-180, 180] deg
  const tilt = ref(0);
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
  const { sourceToDetectorDistance, translation, rotation, tilt } =
    storeToRefs(cArmStore);
  const { metadata } = useImage(imageId);
  const lpsOrientation = computed(() => metadata.value.lpsOrientation);
  const dimensions = computed(() => metadata.value.dimensions);
  const spacing = computed(() => metadata.value.spacing);

  const armTranslation = translation;
  const armRotation = computed(() => -rotation.value);
  const armRotationRad = computed(() => armRotation.value * DEG_TO_RAD);
  const armTilt = tilt;
  const armTiltRad = computed(() => armTilt.value * DEG_TO_RAD);

  const getAxisRange = (axis: number) => {
    const dim = Math.max(
      dimensions.value[axis] * spacing.value[axis],
      sourceToDetectorDistance.value
    );
    return [-1.5 * dim, 1.5 * dim] as const;
  };
  const translationRanges = computed(() => {
    const { Sagittal, Axial, Coronal } = lpsOrientation.value;
    return {
      Sagittal: getAxisRange(Sagittal),
      Coronal: getAxisRange(Coronal),
      Axial: getAxisRange(Axial),
    } as const;
  });

  return {
    armTranslation,
    armRotation,
    armRotationRad,
    armTilt,
    armTiltRad,
    translationRanges,
  };
}

export default useCArmStore;
