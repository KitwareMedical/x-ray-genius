import { View } from '@/src/core/vtk/types';
import { MaybeRef, ref, watchEffect } from 'vue';
import { useGeometryActor2D } from './useActor';
import { useCArmPosition } from './useCArmModel';
import { Maybe } from '@/src/types';
import { Vector3 } from '@kitware/vtk.js/types';
import vtkCubeSource from '@kitware/vtk.js/Filters/Sources/CubeSource';
import { storeToRefs } from 'pinia';
import useCArmStore, { useCArmPhysicalParameters } from '../store/c-arm';

const THICKNESS = 0.000001;

export function useDetectorModel(view: View, imageID: MaybeRef<Maybe<string>>) {
  const { detectorDiameter } = storeToRefs(useCArmStore());
  const { armRotation, armTilt } = useCArmPhysicalParameters(imageID);
  const source = vtkCubeSource.newInstance();
  const geometry = ref(source.getOutputData());
  const { actor } = useGeometryActor2D(view, geometry);
  actor.getProperty().setColor(0, 1, 0);
  actor.getProperty().setOpacity(0.05);

  watchEffect(() => {
    const { detectorPos } = useCArmPosition(imageID);
    const size = detectorDiameter.value;
    source.setXLength(size);
    source.setYLength(THICKNESS);
    source.setZLength(size);
    source.setCenter(...(detectorPos.value as Vector3));
    source.setRotations(armTilt.value, 0, armRotation.value);
    geometry.value = source.getOutputData();
  });
}
