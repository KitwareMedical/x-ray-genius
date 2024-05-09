import { View } from '@/src/core/vtk/types';
import type { vtkObject } from '@kitware/vtk.js/interfaces';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import { watchEffect } from 'vue';

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
