import { useImage } from '@/src/composables/useCurrentImage';
import { Maybe } from '@/src/types';
import vtkViewProxy from '@kitware/vtk.js/Proxy/Core/ViewProxy';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import { Vector3 } from '@kitware/vtk.js/types';
import { computed } from '@vue/reactivity';
import { vec3 } from 'gl-matrix';
import { MaybeRef, unref, watchEffect, watchPostEffect } from 'vue';
import useCArmStore from '../store/c-arm';
import vtkBoundingBox from '@kitware/vtk.js/Common/DataModel/BoundingBox';
import vtkConeSource from '@kitware/vtk.js/Filters/Sources/ConeSource';
import vtkCubeSource from '@kitware/vtk.js/Filters/Sources/CubeSource';

function useActor(viewProxy: MaybeRef<vtkViewProxy>, source: any) {
  const actor = vtkActor.newInstance();
  const mapper = vtkMapper.newInstance();
  mapper.addInputConnection(source.getOutputPort());
  actor.setMapper(mapper);

  watchPostEffect((onCleanup) => {
    const view = unref(viewProxy);
    view.getRenderer().addActor(actor);
    view.renderLater();

    onCleanup(() => {
      view.getRenderer().removeActor(actor);
    });
  });

  return { actor, mapper };
}

function useEmitterPoly(viewProxy: MaybeRef<vtkViewProxy>) {
  const cone = vtkConeSource.newInstance({ radius: 30, height: -60 });
  const { actor } = useActor(viewProxy, cone);
  actor.getProperty().setColor(1, 1, 0);
  return cone;
}

function useDetectorPoly(viewProxy: MaybeRef<vtkViewProxy>) {
  const cube = vtkCubeSource.newInstance({
    xLength: 50,
    yLength: 1,
    zLength: 50,
  });
  const { actor } = useActor(viewProxy, cube);
  actor.getProperty().setColor(1, 0, 0);
  return cube;
}

function useAnchorPoly(viewProxy: MaybeRef<vtkViewProxy>) {
  const cube = vtkCubeSource.newInstance({
    xLength: 30,
    yLength: 30,
    zLength: 30,
  });
  const { actor } = useActor(viewProxy, cube);
  actor.getProperty().setColor(1, 1, 1);
  return cube;
}

export function useCArm(
  viewProxy: MaybeRef<vtkViewProxy>,
  imageID: MaybeRef<Maybe<string>>,
  radius: MaybeRef<number>
) {
  const emitterPoly = useEmitterPoly(viewProxy);
  const detectorPoly = useDetectorPoly(viewProxy);
  const anchorPoly = useAnchorPoly(viewProxy);

  const { metadata } = useImage(imageID);
  const imageCenter = computed(() => {
    return vtkBoundingBox.getCenter(metadata.value.worldBounds) as vec3;
  });
  const dimensions = computed(() => metadata.value.dimensions);

  const defaultEmitterVec = [0, -1, 0] as Vector3; // Anterior
  const defaultAnchorVec = [-1, 0, 0] as Vector3; // Right

  const cArmStore = useCArmStore();
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
  // X/Sagittal
  const xTranslation = computed(() => {
    return (cArmStore.xTranslation - 0.5) * dimensions.value[0];
  });
  // Z/Axial
  const zTranslation = computed(() => {
    return (cArmStore.zTranslation - 0.5) * dimensions.value[2];
  });

  const emitterVec = computed(() => {
    const vec = vec3.create();
    vec3.copy(vec, defaultEmitterVec);
    vec3.rotateZ(vec, vec, [0, 0, 0], armRotation.value);
    vec3.rotateX(vec, vec, [0, 0, 0], armTilt.value);
    return vec;
  });

  const detectorVec = computed(() => {
    const vec = vec3.create();
    vec3.negate(vec, emitterVec.value);
    return vec as Vector3;
  });

  const transformToWorldPos = (vec: vec3) => {
    const pos = vec3.create();
    vec3.scale(pos, vec, unref(radius));
    vec3.add(pos, pos, imageCenter.value);
    vec3.add(pos, pos, [xTranslation.value, 0, zTranslation.value]);
    return pos as Vector3;
  };

  const emitterPos = computed(() => transformToWorldPos(emitterVec.value));
  const detectorPos = computed(() => transformToWorldPos(detectorVec.value));
  const anchorPos = computed(() => transformToWorldPos(defaultAnchorVec));

  watchEffect(() => {
    emitterPoly.setCenter(...emitterPos.value);
    // points towards detector
    emitterPoly.setDirection(...detectorVec.value);

    detectorPoly.setCenter(...detectorPos.value);
    detectorPoly.setRotations(armTiltDeg.value, 0, armRotationDeg.value);

    anchorPoly.setCenter(...anchorPos.value);
    anchorPoly.setRotations(armTiltDeg.value, 0, 0);

    unref(viewProxy).renderLater();
  });
}
