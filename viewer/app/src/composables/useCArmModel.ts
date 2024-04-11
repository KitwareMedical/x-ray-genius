import type { vtkObject } from '@kitware/vtk.js/interfaces';
import { useImage } from '@/src/composables/useCurrentImage';
import { Maybe } from '@/src/types';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import { Vector3 } from '@kitware/vtk.js/types';
import { computed } from '@vue/reactivity';
import { mat4, quat, vec3 } from 'gl-matrix';
import { MaybeRef, watchEffect, toRef } from 'vue';
import useCArmStore, { useCArmPhysicalParameters } from '../store/c-arm';
import vtkBoundingBox from '@kitware/vtk.js/Common/DataModel/BoundingBox';
import { storeToRefs } from 'pinia';
import { View } from '@/src/core/vtk/types';
import vtkOBJReader from '@kitware/vtk.js/IO/Misc/OBJReader';

import CArmObj from '../../assets/c-arm-edited-2.obj?raw';
import { ImageMetadata } from '@/src/types/image';

// approximate distance for an unscaled model (mm)
const MODEL_SOURCE_TO_DETECTOR_DISTANCE = 1.22;

function getFlipFactors(metadata: ImageMetadata) {
  const { orientation, lpsOrientation } = metadata;
  const { Left, Posterior, Superior, Coronal, Sagittal, Axial } =
    lpsOrientation;
  const sVec = orientation.slice(Sagittal * 3, Sagittal * 3 + 3) as vec3;
  const cVec = orientation.slice(Coronal * 3, Coronal * 3 + 3) as vec3;
  const aVec = orientation.slice(Axial * 3, Axial * 3 + 3) as vec3;
  return [
    Math.sign(vec3.dot(sVec, Left)),
    Math.sign(vec3.dot(cVec, Posterior)),
    Math.sign(vec3.dot(aVec, Superior)),
  ] as Vector3;
}

function useActor(view: View, source: vtkObject) {
  const actor = vtkActor.newInstance();
  const mapper = vtkMapper.newInstance();
  mapper.setInputData(source);
  actor.setMapper(mapper);

  watchEffect((onCleanup) => {
    const { renderer } = view;
    renderer.addActor(actor);
    view.requestRender();

    onCleanup(() => {
      renderer.removeActor(actor);
    });
  });

  return { actor, mapper };
}

function loadModel() {
  const reader = vtkOBJReader.newInstance();
  reader.parseAsText(CArmObj);
  return reader.getOutputData(0);
}

export function useCArmPosition(imageID: MaybeRef<Maybe<string>>) {
  const { metadata } = useImage(imageID);
  const imageCenter = computed(() => {
    return vtkBoundingBox.getCenter(metadata.value.worldBounds) as vec3;
  });

  const defaultLpsEmitterPos = [0, 1, 0] as Vector3; // Posterior
  const defaultLpsEmitterUpDir = [0, 0, 1] as Vector3; // Superior
  const defaultLpsAnchorDir = [-1, 0, 0] as Vector3; // Right

  const cArmStore = useCArmStore();
  const { sourceToDetectorDistance, detectorDiameter } = storeToRefs(cArmStore);
  const { armTranslation, armRotation, armRotationDeg, armTilt, armTiltDeg } =
    useCArmPhysicalParameters(imageID);

  const lpsEmitterPos = computed(() => {
    const vec = vec3.create();
    vec3.copy(vec, defaultLpsEmitterPos);
    vec3.rotateZ(vec, vec, [0, 0, 0], armRotation.value);
    vec3.rotateX(vec, vec, [0, 0, 0], -armTilt.value);
    return vec as Vector3;
  });

  // direction that the emitter emits xrays
  const emitterDir = computed(() => {
    const vec = vec3.create();
    vec3.negate(vec, lpsEmitterPos.value);
    return vec as Vector3;
  });

  const emitterUpDir = computed(() => {
    const vec = vec3.create();
    vec3.copy(vec, defaultLpsEmitterUpDir);
    vec3.rotateX(vec, vec, [0, 0, 0], -armTilt.value);
    return vec as Vector3;
  });

  const transformToWorldPos = (vec: vec3) => {
    const pos = vec3.create();
    vec3.scale(pos, vec, sourceToDetectorDistance.value / 2);
    vec3.add(pos, pos, imageCenter.value);
    vec3.add(pos, pos, armTranslation.value);
    return pos as Vector3;
  };

  const centerPos = computed(() => {
    const pos = vec3.create();
    vec3.add(pos, pos, armTranslation.value);
    return pos as Vector3;
  });

  const emitterPos = computed(() => transformToWorldPos(lpsEmitterPos.value));
  const anchorPos = computed(() => transformToWorldPos(defaultLpsAnchorDir));

  return {
    emitterPos,
    anchorPos,
    centerPos,
    armTiltDeg,
    armTilt,
    armRotationDeg,
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
  const { actor } = useActor(view, geometry);

  const { centerPos, armTilt, armRotation } = useCArmPosition(imageID);

  const { sourceToDetectorDistance } = storeToRefs(useCArmStore());

  const { metadata } = useImage(imageID);
  const imageCenter = computed(() =>
    vtkBoundingBox.getCenter(metadata.value.worldBounds)
  );

  const imageDirQuat = computed(() => {
    const rot = quat.create();
    quat.fromMat3(rot, metadata.value.orientation);
    return rot;
  });

  const modelCenter = computed(() => {
    const out = vec3.create();
    vec3.add(out, centerPos.value, imageCenter.value);
    return out as Vector3;
  });

  const modelToImage = computed(() => {
    const t = mat4.create();
    mat4.fromRotationTranslation(t, imageDirQuat.value, modelCenter.value);
    return t;
  });

  watchEffect(() => {
    /**
     * Model orientation: detector is in Posterior (+Y for vtk.js (LPS)) direction.
     *
     * Viewer: viewUp is Anterior. Detector should be in the Anterior direction, facing down to Posterior.
     */
    const size =
      sourceToDetectorDistance.value / MODEL_SOURCE_TO_DETECTOR_DISTANCE;

    const scaleFactors = getFlipFactors(metadata.value);
    // flip Y axis so detector points Anterior->Posterior.
    scaleFactors[1] *= -1;
    actor.setScale(...(scaleFactors.map((v) => v * size) as Vector3));

    const mm = mat4.create();
    // rotate Z, then X
    mat4.rotateX(mm, mm, armTilt.value);
    mat4.rotateZ(mm, mm, armRotation.value);
    // apply model-to-image transform last
    mat4.mul(mm, modelToImage.value, mm);
    actor.setUserMatrix(mm);

    view.renderer.resetCameraClippingRange();
    view.requestRender();
  });
}
