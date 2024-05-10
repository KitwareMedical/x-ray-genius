import { MaybeRef, watchEffect } from 'vue';
import useCArmStore from '../store/c-arm';
import { useCArmPosition } from './useCArmModel';
import { Maybe } from '@/src/types';
import { storeToRefs } from 'pinia';
import { View } from '@/src/core/vtk/types';
import { vtkFieldRef } from '@/src/core/vtk/vtkFieldRef';

const RAD_TO_DEG = 180 / Math.PI;
const VIEW_ANGLE_BORDER_FACTOR = 1.1;

export function useCArmCamera(view: View, imageID: MaybeRef<Maybe<string>>) {
  const { detectorDiameter, sourceToDetectorDistance } = storeToRefs(
    useCArmStore()
  );

  const { emitterPos, centerPos, emitterDir, emitterUpDir } =
    useCArmPosition(imageID);
  const size = vtkFieldRef(view.renderWindowView, 'size');

  watchEffect(() => {
    const emitterViewAngle =
      2 *
      Math.atan2(detectorDiameter.value / 2, sourceToDetectorDistance.value);

    const [width, height] = size.value;
    const aspect = width / height;
    // Camera view angle is the vertical view angle
    let cameraViewAngle = emitterViewAngle;
    if (width < height) {
      // To keep the entire detector in the view, treat emitterViewAngle as
      // the horizontal camera view angle.
      // similar triangles: width = aspect, height = 1
      const x = aspect / 2 / Math.tan(emitterViewAngle / 2);
      cameraViewAngle = 2 * Math.atan2(0.5, x);
    }

    const cam = view.renderer.getActiveCamera();
    cam.setPosition(...emitterPos.value);
    cam.setDirectionOfProjection(...emitterDir.value);
    cam.setViewUp(...emitterUpDir.value);
    cam.setFocalPoint(...centerPos.value);
    cam.setViewAngle(cameraViewAngle * RAD_TO_DEG * VIEW_ANGLE_BORDER_FACTOR);

    view.renderer.resetCameraClippingRange();
    view.requestRender();
  });
}
