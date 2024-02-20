import { Layout, LayoutDirection } from '@/src/types/layout';
import { InitViewIDs, InitViewSpecs, Layouts } from '@/src/config';

export * from '@/src/config';

export const DefaultLayoutName = 'Simulation View';

InitViewIDs.GantryView = 'GantryView';
InitViewIDs.XRayView = 'XRayView';

InitViewSpecs[InitViewIDs.GantryView] = {
  viewType: 'Gantry',
  props: {
    viewDirection: 'Posterior',
    viewUp: 'Superior',
  },
};

InitViewSpecs[InitViewIDs.XRayView] = {
  viewType: 'XRay',
  props: {},
};

Layouts[DefaultLayoutName] = {
  name: DefaultLayoutName,
  direction: LayoutDirection.V,
  items: [InitViewIDs.GantryView, InitViewIDs.XRayView],
};

export { Layouts, InitViewIDs };
