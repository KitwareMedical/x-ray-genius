import { MaybeRef, watchEffect } from 'vue';
import useCArmStore from '../store/c-arm';
import { useCArmPosition } from './useCArmModel';
import { Maybe } from '@/src/types';
import { storeToRefs } from 'pinia';
import { View } from '@/src/core/vtk/types';

const RAD_TO_DEG = 180 / Math.PI;

export function useCArmCamera(view: View, imageID: MaybeRef<Maybe<string>>) {
  const { detectorDiameter, sourceToDetectorDistance } = storeToRefs(
    useCArmStore()
  );

  const { detectorPos, emitterDir, detectorUpDir } = useCArmPosition(imageID);

  watchEffect(() => {
    const viewAngle =
      RAD_TO_DEG *
      2 *
      Math.atan2(detectorDiameter.value / 2, sourceToDetectorDistance.value);

    const cam = view.renderer.getActiveCamera();
    cam.setPosition(...detectorPos.value);
    cam.setDirectionOfProjection(...emitterDir.value);
    cam.setViewUp(...detectorUpDir.value);
    cam.setViewAngle(viewAngle);

    view.renderer.resetCameraClippingRange();
    view.requestRender();
  });
}
