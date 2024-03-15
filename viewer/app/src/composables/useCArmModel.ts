import type { vtkObject } from '@kitware/vtk.js/interfaces';
import { useImage } from '@/src/composables/useCurrentImage';
import { Maybe } from '@/src/types';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import { Vector3 } from '@kitware/vtk.js/types';
import { computed } from '@vue/reactivity';
import { mat4, quat, vec3 } from 'gl-matrix';
import { MaybeRef, watchEffect, toRef } from 'vue';
import useCArmStore from '../store/c-arm';
import vtkBoundingBox from '@kitware/vtk.js/Common/DataModel/BoundingBox';
import { storeToRefs } from 'pinia';
import { View } from '@/src/core/vtk/useVtkView';
import vtkOBJReader from '@kitware/vtk.js/IO/Misc/OBJReader';

import CArmObj from '../../assets/c-arm-edited-2.obj?raw';

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

export function useCArmPosition(view: View, imageID: MaybeRef<Maybe<string>>) {
  const { metadata } = useImage(imageID);
  const imageCenter = computed(() => {
    return vtkBoundingBox.getCenter(metadata.value.worldBounds) as vec3;
  });
  const dimensions = computed(() => metadata.value.dimensions);

  const defaultEmitterDir = [0, -1, 0] as Vector3; // Anterior
  const defaultEmitterUpDir = [0, 0, 1] as Vector3; // Superior
  const defaultAnchorDir = [-1, 0, 0] as Vector3; // Right

  const cArmStore = useCArmStore();
  const { sourceToDetectorDistance, detectorDiameter } = storeToRefs(cArmStore);
  // rotation angle around Z
  const armRotation = computed(() => {
    // map [0,1] to [-0.5,0.5] * range
    return (cArmStore.rotation - 0.5) * (0.9 * 2 * Math.PI);
  });
  const armRotationDeg = computed(() => (armRotation.value * 180) / Math.PI);
  // tilt angle around X
  const armTilt = computed(() => {
    // map [0,1] to [-0.5,0.5] * range
    return (cArmStore.tilt - 0.5) * Math.PI;
  });
  const armTiltDeg = computed(() => (armTilt.value * 180) / Math.PI);
  const armTranslation = computed(() => {
    return cArmStore.translation.map(
      (v, i) => (v - 0.5) * dimensions.value[i]
    ) as Vector3;
  });

  // origin -> emitter
  const emitterDir = computed(() => {
    const vec = vec3.create();
    vec3.copy(vec, defaultEmitterDir);
    vec3.rotateZ(vec, vec, [0, 0, 0], armRotation.value);
    vec3.rotateX(vec, vec, [0, 0, 0], armTilt.value);
    return vec as Vector3;
  });

  const emitterUpDir = computed(() => {
    const vec = vec3.create();
    vec3.copy(vec, defaultEmitterUpDir);
    vec3.rotateX(vec, vec, [0, 0, 0], armTilt.value);
    return vec as Vector3;
  });

  // origin -> detector
  const detectorDir = computed(() => {
    const vec = vec3.create();
    vec3.negate(vec, emitterDir.value);
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

  const emitterPos = computed(() => transformToWorldPos(emitterDir.value));
  const detectorPos = computed(() => transformToWorldPos(detectorDir.value));
  const anchorPos = computed(() => transformToWorldPos(defaultAnchorDir));

  return {
    emitterPos,
    detectorPos,
    anchorPos,
    centerPos,
    armTiltDeg,
    armTilt,
    armRotationDeg,
    armRotation,
    detectorDiameter,
    detectorDir,
    emitterDir,
    emitterUpDir,
    anchorDir: toRef(defaultAnchorDir),
  };
}

export function useCArmModel(view: View, imageID: MaybeRef<Maybe<string>>) {
  const geometry = loadModel();
  const { actor } = useActor(view, geometry);

  const { centerPos, armTilt, armRotation } = useCArmPosition(view, imageID);

  const { detectorDiameter } = storeToRefs(useCArmStore());

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
    const size = detectorDiameter.value * 1.5;
    actor.setScale(size, size, size);

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
