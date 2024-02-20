import { ViewTypeToComponent } from '@/src/core/viewTypes';
import GantryView from '../components/GantryView.vue';
import XRayView from '../components/XRayView.vue';

ViewTypeToComponent.Gantry = GantryView;
ViewTypeToComponent.XRay = XRayView;

export { ViewTypeToComponent };
