import { hyphenate } from '@vueuse/core';
import { storeToRefs } from 'pinia';
import useCArmStore, { useCArmPhysicalParameters } from './store/c-arm';
import { useCurrentImage, useImage } from '@/src/composables/useCurrentImage';
import { computed } from 'vue';

function parseSessionUuid() {
  const parts = window.location.pathname.replace(/\/+/, '/').split('/');
  const idx = parts.indexOf('session');
  if (idx < 0) return null;
  const uuid = parts[idx + 1];
  return uuid ?? null;
}

export const ENDPOINT = import.meta.env.VITE_API_ENDPOINT;
export const SESSION_UUID = parseSessionUuid();

if (!ENDPOINT) console.warn('No API endpoint specified!');
if (!SESSION_UUID) console.warn('No session UUID!');

function getParameterUrl(sessionPk: string) {
  return `${ENDPOINT}/session/${sessionPk}/parameters/`;
}

export interface CArmParameters {
  carmAlpha?: number;
  carmAlphaKappa?: number;
  carmBeta?: number;
  carmBetaKappa?: number;
  carmPushPullTranslation?: number;
  carmHeadFootTranslation?: number;
  carmRaiseLowerTranslation?: number;
  carmPushPullStdDev?: number;
  carmHeadFootStdDev?: number;
  carmRaiseLowerStdDev?: number;
  sourceToDetectorDistance: number;
  detectorDiameter: number;
  numSamples: number;
}

function snakeify(s: string) {
  return hyphenate(s).replaceAll(/-/g, '_');
}

function snakeifyObject(obj: Record<string, any>) {
  return Object.entries(obj).reduce(
    (result, [key, value]) => ({ ...result, [snakeify(key)]: value }),
    {} as Record<string, any>
  );
}

function kappaStdDevToConcentration(sdev: number) {
  return 1 / ((Math.PI / 180) * sdev) ** 2;
}

export function exportApiParameters(): CArmParameters {
  const {
    randomizeRotation,
    rotation,
    rotationKappaStdDev,
    randomizeTilt,
    tilt,
    tiltKappaStdDev,
    translation: relativeTranslation,
    randomizeX,
    randomizeY,
    randomizeZ,
    randStdDevX,
    randStdDevY,
    randStdDevZ,
    sourceToDetectorDistance,
    numberOfSamples,
    detectorDiameter,
  } = storeToRefs(useCArmStore());

  const { currentImageID, currentImageMetadata } = useCurrentImage();
  const dimensions = computed(() => currentImageMetadata.value.dimensions);
  const translation = computed(() => {
    return relativeTranslation.value.map((v, i) => v * dimensions.value[i]);
  });

  const { armTranslation, armRotation, armTilt } =
    useCArmPhysicalParameters(currentImageID);

  return {
    carmAlpha: randomizeRotation.value ? undefined : armRotation.value,
    carmAlphaKappa: kappaStdDevToConcentration(rotationKappaStdDev.value),
    carmBeta: randomizeTilt.value ? undefined : armTilt.value,
    carmBetaKappa: kappaStdDevToConcentration(tiltKappaStdDev.value),
    carmPushPullTranslation: armTranslation.value[0],
    carmRaiseLowerTranslation: armTranslation.value[1],
    carmHeadFootTranslation: armTranslation.value[2],
    carmPushPullStdDev: randomizeX.value ? randStdDevX.value : undefined,
    carmRaiseLowerStdDev: randomizeY.value ? randStdDevY.value : undefined,
    carmHeadFootStdDev: randomizeZ.value ? randStdDevZ.value : undefined,
    sourceToDetectorDistance: sourceToDetectorDistance.value,
    detectorDiameter: detectorDiameter.value,
    numSamples: numberOfSamples.value || 100,
  };
}

export function postCArmParameters(param: CArmParameters) {
  if (!SESSION_UUID) throw new Error('No session UUID');

  const headers = new Headers({
    'content-type': 'application/json',
  });
  const body = JSON.stringify(snakeifyObject(param));
  return fetch(getParameterUrl(SESSION_UUID), {
    method: 'POST',
    headers,
    body,
  });
}
