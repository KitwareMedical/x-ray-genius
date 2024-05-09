import { Maybe } from '@/src/types';
import { Vector3 } from '@kitware/vtk.js/types';
import { computed } from '@vue/reactivity';
import { mat4, vec3 } from 'gl-matrix';
import { MaybeRef, watchEffect, toRef } from 'vue';
import useCArmStore, { useCArmPhysicalParameters } from '../store/c-arm';
import { storeToRefs } from 'pinia';
import { View } from '@/src/core/vtk/types';
import vtkOBJReader from '@kitware/vtk.js/IO/Misc/OBJReader';

import CArmObj from '../../assets/c-arm-edited-2.obj?raw';
import { useGeometryActor } from './useActor';

// approximate distance for an unscaled model (mm)
const MODEL_SOURCE_TO_DETECTOR_DISTANCE = 1.22;

function loadModel() {
  const reader = vtkOBJReader.newInstance();
  reader.parseAsText(CArmObj);
  return reader.getOutputData(0);
}

export function useCArmPosition(imageID: MaybeRef<Maybe<string>>) {
  const defaultLpsEmitterPos = [0, 1, 0] as Vector3; // Posterior
  const defaultLpsEmitterUpDir = [0, 0, 1] as Vector3; // Superior
  const defaultLpsAnchorDir = [-1, 0, 0] as Vector3; // Right

  const cArmStore = useCArmStore();
  const { sourceToDetectorDistance, detectorDiameter } = storeToRefs(cArmStore);
  const { armTranslation, armRotation, armRotationRad, armTilt, armTiltRad } =
    useCArmPhysicalParameters(imageID);

  const rotatedNormalizedEmitterPos = computed(() => {
    const pos = vec3.create();
    vec3.copy(pos, defaultLpsEmitterPos);
    vec3.rotateZ(pos, pos, [0, 0, 0], armRotationRad.value);
    vec3.rotateX(pos, pos, [0, 0, 0], armTiltRad.value);
    return pos as Vector3;
  });

  const emitterPos = computed(() => {
    const pos = vec3.create();
    vec3.copy(pos, rotatedNormalizedEmitterPos.value);
    vec3.scale(pos, pos, sourceToDetectorDistance.value / 2);
    vec3.add(pos, pos, armTranslation.value);
    return pos as Vector3;
  });

  // direction that the emitter emits xrays
  const emitterDir = computed(() => {
    const dir = vec3.create();
    vec3.negate(dir, rotatedNormalizedEmitterPos.value);
    return dir as Vector3;
  });

  const emitterUpDir = computed(() => {
    const dir = vec3.create();
    vec3.copy(dir, defaultLpsEmitterUpDir);
    vec3.rotateX(dir, dir, [0, 0, 0], armTiltRad.value);
    return dir as Vector3;
  });

  const centerPos = armTranslation;
  const anchorPos = defaultLpsAnchorDir;
  const detectorPos = computed(() => {
    const pos = vec3.create();
    const fromEmitterToDetector = vec3.create();
    vec3.scale(
      fromEmitterToDetector,
      emitterDir.value,
      sourceToDetectorDistance.value
    );
    vec3.add(pos, emitterPos.value, fromEmitterToDetector);
    return pos;
  });

  return {
    detectorPos,
    emitterPos,
    anchorPos,
    centerPos,
    armTiltRad,
    armTilt,
    armRotationRad,
    armRotation,
    detectorDiameter,
    emitterDir,
    detectorUpDir: emitterUpDir,
    emitterUpDir,
    anchorDir: toRef(defaultLpsAnchorDir),
  };
}

export function useCArmModel(view: View, imageID: MaybeRef<Maybe<string>>) {
  const geometry = loadModel();
  const { actor } = useGeometryActor(view, geometry);

  const { centerPos, armTiltRad, armRotationRad } = useCArmPosition(imageID);

  const { sourceToDetectorDistance } = storeToRefs(useCArmStore());

  watchEffect(() => {
    /**
     * Model orientation: detector is in Posterior (+Y for vtk.js (LPS)) direction.
     *
     * Viewer: viewUp is Anterior. Detector should be in the Anterior direction, facing down to Posterior.
     */
    const size =
      sourceToDetectorDistance.value / MODEL_SOURCE_TO_DETECTOR_DISTANCE;

    // flip Y axis so detector points Anterior->Posterior.
    actor.setScale(size, -size, size);

    const mm = mat4.create();
    // order of transforms: rotate Z, then X, then translate
    // UserMatrix = M_translate * M_rotateX * M_rotateZ
    mat4.translate(mm, mm, centerPos.value);
    mat4.rotateX(mm, mm, armTiltRad.value);
    mat4.rotateZ(mm, mm, armRotationRad.value);
    actor.setUserMatrix(mm);

    view.renderer.resetCameraClippingRange();
    view.requestRender();
  });
}
