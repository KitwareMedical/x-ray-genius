import vtkViewProxy from '@kitware/vtk.js/Proxy/Core/ViewProxy';
import { MaybeRef, computed, unref, watchEffect } from 'vue';
import useCArmStore from '../store/c-arm';
import { useCArmPosition } from './useCArmModel';
import { Maybe } from '@/src/types';
import { vec3 } from 'gl-matrix';
import { Vector3 } from '@kitware/vtk.js/types';

export function useCArmCamera(
  viewProxy: MaybeRef<vtkViewProxy>,
  imageID: MaybeRef<Maybe<string>>
) {
  const camera = computed(() => unref(viewProxy).getCamera());
  const store = useCArmStore();

  const { emitterPos, detectorDir, anchorDir } = useCArmPosition(
    viewProxy,
    imageID
  );

  watchEffect(() => {
    const viewUp = vec3.create() as Vector3;
    vec3.cross(viewUp, detectorDir.value, anchorDir.value);

    const cam = unref(camera);
    cam.setPosition(...emitterPos.value);
    cam.setDirectionOfProjection(...detectorDir.value);
    cam.setViewUp(...viewUp);

    unref(viewProxy).renderLater();
  });
}
