import vtkViewProxy from '@kitware/vtk.js/Proxy/Core/ViewProxy';
import { MaybeRef, computed, unref, watchEffect } from 'vue';
import useCArmStore from '../store/c-arm';
import { useCArmPosition } from './useCArmModel';
import { Maybe } from '@/src/types';
import { storeToRefs } from 'pinia';
import { View } from '@/src/core/vtk/useVtkView';

export function useCArmCamera(view: View, imageID: MaybeRef<Maybe<string>>) {
  const { detectorDiameter, sourceToDetectorDistance } = storeToRefs(
    useCArmStore()
  );

  const { emitterPos, detectorDir, emitterUpDir } = useCArmPosition(imageID);

  watchEffect(() => {
    const viewAngle =
      (180 / Math.PI) *
      2 *
      Math.atan2(detectorDiameter.value / 2, sourceToDetectorDistance.value);

    const cam = view.renderer.getActiveCamera();
    cam.setPosition(...emitterPos.value);
    cam.setDirectionOfProjection(...detectorDir.value);
    cam.setViewUp(...emitterUpDir.value);
    cam.setViewAngle(viewAngle * 4);

    view.renderer.resetCameraClippingRange();
    view.requestRender();
  });
}
