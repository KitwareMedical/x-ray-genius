import { View } from '@/src/core/vtk/types';
import type { vtkObject } from '@kitware/vtk.js/interfaces';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkActor2D from '@kitware/vtk.js/Rendering/Core/Actor2D';
import vtkCoordinate from '@kitware/vtk.js/Rendering/Core/Coordinate';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkMapper2D from '@kitware/vtk.js/Rendering/Core/Mapper2D';
import { DisplayLocation } from '@kitware/vtk.js/Rendering/Core/Property2D/Constants';
import { MaybeRef, unref, watchEffect } from 'vue';

export function useGeometryActor(view: View, source: vtkObject) {
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

export function useGeometryActor2D(view: View, source: MaybeRef<vtkObject>) {
  const actor = vtkActor2D.newInstance();
  const mapper = vtkMapper2D.newInstance();
  const coordinate = vtkCoordinate.newInstance();

  coordinate.setCoordinateSystemToWorld();
  mapper.setTransformCoordinate(coordinate);
  actor.setMapper(mapper);
  actor.setCoordinateSystemToWorld();
  actor.getProperty().setDisplayLocation(DisplayLocation.FOREGROUND);

  watchEffect(() => {
    mapper.setInputData(unref(source));
  });

  watchEffect((onCleanup) => {
    const { renderer } = view;
    renderer.addActor2D(actor);
    view.requestRender();

    onCleanup(() => {
      renderer.removeActor2D(actor);
    });
  });

  return { actor, mapper };
}
