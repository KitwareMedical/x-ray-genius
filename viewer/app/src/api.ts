import { hyphenate } from '@vueuse/core';

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
  carmAlpha: number;
  carmBeta: number;
  sourceToDetectorDistance: number;
}

function snakeify(s: string) {
  return hyphenate(s).replace(/-/, '_');
}

function snakeifyObject(obj: Record<string, any>) {
  return Object.entries(obj).reduce(
    (result, [key, value]) => ({ ...result, [snakeify(key)]: value }),
    {} as Record<string, any>
  );
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
