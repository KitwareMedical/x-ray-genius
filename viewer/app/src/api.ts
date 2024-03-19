import { hyphenate } from '@vueuse/core';
import { storeToRefs } from 'pinia';
import useCArmStore from './store/c-arm';
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

export function exportApiParameters(): CArmParameters {
  const {
    randomizeRotation,
    rotation,
    rotationKappa,
    randomizeTilt,
    tilt,
    tiltKappa,
    translation: relativeTranslation,
    randomizeX,
    randomizeY,
    randomizeZ,
    randStdDevX,
    randStdDevY,
    randStdDevZ,
    sourceToDetectorDistance,
    numberOfSamples,
  } = storeToRefs(useCArmStore());

  const { currentImageMetadata } = useCurrentImage();
  const dimensions = computed(() => currentImageMetadata.value.dimensions);
  const translation = computed(() => {
    return relativeTranslation.value.map((v, i) => v * dimensions.value[i]);
  });

  return {
    carmAlpha: randomizeRotation.value
      ? undefined
      : rotation.value * 2 * Math.PI,
    carmAlphaKappa: rotationKappa.value,
    carmBeta: randomizeTilt.value ? undefined : tilt.value * 2 * Math.PI,
    carmBetaKappa: tiltKappa.value,
    carmPushPullTranslation: translation.value[0],
    carmRaiseLowerTranslation: translation.value[1],
    carmHeadFootTranslation: translation.value[2],
    carmPushPullStdDev: randomizeX.value ? randStdDevX.value : undefined,
    carmRaiseLowerStdDev: randomizeY.value ? randStdDevY.value : undefined,
    carmHeadFootStdDev: randomizeZ.value ? randStdDevZ.value : undefined,
    sourceToDetectorDistance: sourceToDetectorDistance.value,
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
