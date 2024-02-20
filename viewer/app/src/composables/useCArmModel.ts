import { useImage } from '@/src/composables/useCurrentImage';
import { Maybe } from '@/src/types';
import vtkViewProxy from '@kitware/vtk.js/Proxy/Core/ViewProxy';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import { Vector3 } from '@kitware/vtk.js/types';
import { computed } from '@vue/reactivity';
import { vec3 } from 'gl-matrix';
import { MaybeRef, unref, watchEffect, watchPostEffect, toRef } from 'vue';
import useCArmStore from '../store/c-arm';
import vtkBoundingBox from '@kitware/vtk.js/Common/DataModel/BoundingBox';
import vtkConeSource from '@kitware/vtk.js/Filters/Sources/ConeSource';
import vtkCubeSource from '@kitware/vtk.js/Filters/Sources/CubeSource';
import { storeToRefs } from 'pinia';

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

export function useCArmPosition(
  viewProxy: MaybeRef<vtkViewProxy>,
  imageID: MaybeRef<Maybe<string>>
) {
  const { metadata } = useImage(imageID);
  const imageCenter = computed(() => {
    return vtkBoundingBox.getCenter(metadata.value.worldBounds) as vec3;
  });
  const dimensions = computed(() => metadata.value.dimensions);

  const defaultEmitterDir = [0, -1, 0] as Vector3; // Anterior
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
    return vec;
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

  const emitterPos = computed(() => transformToWorldPos(emitterDir.value));
  const detectorPos = computed(() => transformToWorldPos(detectorDir.value));
  const anchorPos = computed(() => transformToWorldPos(defaultAnchorDir));

  return {
    emitterPos,
    detectorPos,
    anchorPos,
    armTiltDeg,
    armRotationDeg,
    detectorDiameter,
    detectorDir,
    emitterDir,
    anchorDir: toRef(defaultAnchorDir),
  };
}

export function useCArmModel(
  viewProxy: MaybeRef<vtkViewProxy>,
  imageID: MaybeRef<Maybe<string>>
) {
  const emitterPoly = useEmitterPoly(viewProxy);
  const detectorPoly = useDetectorPoly(viewProxy);
  const anchorPoly = useAnchorPoly(viewProxy);

  const {
    emitterPos,
    detectorPos,
    anchorPos,
    detectorDiameter,
    detectorDir,
    armTiltDeg,
    armRotationDeg,
  } = useCArmPosition(viewProxy, imageID);

  watchEffect(() => {
    emitterPoly.setCenter(...emitterPos.value);
    // points towards detector
    emitterPoly.setDirection(...detectorDir.value);

    detectorPoly.setCenter(...detectorPos.value);
    detectorPoly.setRotations(armTiltDeg.value, 0, armRotationDeg.value);
    detectorPoly.setXLength(detectorDiameter.value);
    detectorPoly.setZLength(detectorDiameter.value);

    anchorPoly.setCenter(...anchorPos.value);
    anchorPoly.setRotations(armTiltDeg.value, 0, 0);

    unref(viewProxy).renderLater();
  });
}
