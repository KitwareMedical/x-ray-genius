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
  carmAlphaKappa?: number | null;
  carmBeta?: number;
  carmBetaKappa?: number | null;
  carmPushPullTranslation?: number;
  carmHeadFootTranslation?: number;
  carmRaiseLowerTranslation?: number;
  carmPushPullStdDev?: number | null;
  carmHeadFootStdDev?: number | null;
  carmRaiseLowerStdDev?: number | null;
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
    rotation,
    randomizeRotation,
    rotationKappaStdDev,
    tilt,
    randomizeTilt,
    tiltKappaStdDev,
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

  const { currentImageID } = useCurrentImage();

  const { armTranslation } = useCArmPhysicalParameters(currentImageID);

  return {
    carmAlpha: rotation.value,
    carmAlphaKappa: randomizeRotation.value
      ? kappaStdDevToConcentration(rotationKappaStdDev.value)
      : null,
    carmBeta: tilt.value,
    carmBetaKappa: randomizeTilt.value
      ? kappaStdDevToConcentration(tiltKappaStdDev.value)
      : null,
    carmPushPullTranslation: armTranslation.value[0],
    carmRaiseLowerTranslation: armTranslation.value[1],
    carmHeadFootTranslation: armTranslation.value[2],
    carmPushPullStdDev: randomizeX.value ? randStdDevX.value : null,
    carmRaiseLowerStdDev: randomizeY.value ? randStdDevY.value : null,
    carmHeadFootStdDev: randomizeZ.value ? randStdDevZ.value : null,
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
