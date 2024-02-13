<script setup lang="ts">
import '@/src/vtk/ColorMaps';
import { useEventListener } from '@vueuse/core';
import { computed } from 'vue';
import { toRefs } from 'vue';
import { ref, onMounted } from 'vue';

interface Props {
  size: number;
}

const props = defineProps<Props>();
const { size } = toRefs(props);

const percentModel = defineModel({ default: 0.5 });

const cArmPath = ref<SVGPathElement | undefined>();
const svg = ref<SVGElement | undefined>();
const radius = computed(() => size.value / 4);
const cx = computed(() => size.value / 2);
const cy = computed(() => size.value / 2);
const gap = computed(() => size.value / 4);
const gapAngle = computed(() => 2 * Math.asin(gap.value / 2 / radius.value)); // rad

// coordinate system starts at top-left with +y going down
const Mx = computed(() => cx.value - gap.value / 2);
const My = computed(
  () => cy.value + Math.sqrt(radius.value ** 2 - (gap.value / 2) ** 2)
);

// x, y expected to be in SVG coordinates
function percentAlongGaugeArc(x: number, y: number) {
  // get normalized vector to x,y
  const dx = cx.value - x;
  const dy = cy.value - y;
  const len = Math.sqrt(dx * dx + dy * dy);
  const nx = dx / len;
  const ny = dy / len;
  // get angle from svg +y vertical
  const angle = Math.acos(0 * nx - 1 * ny);
  // get left/right via cross product
  const side = Math.sign(0 * ny - nx * -1);
  const angleAlongCircle = side === 1 ? angle : 2 * Math.PI - angle;
  // get percent of the path along arc
  const minAngle = gapAngle.value / 2;
  const maxAngle = 2 * Math.PI - minAngle;
  const constrainedAngle = Math.max(
    minAngle,
    Math.min(maxAngle, angleAlongCircle)
  );
  const percentAlongPath =
    (constrainedAngle - minAngle) / (maxAngle - minAngle);
  return percentAlongPath;
}

const handleX = ref(0);
const handleY = ref(0);
const dragging = ref(false);

function drawCArmMarker(percent: number) {
  if (!cArmPath.value) return;
  const el = cArmPath.value;
  const len = el.getTotalLength();
  const pt = el.getPointAtLength(percent * len);
  handleX.value = pt.x;
  handleY.value = pt.y;
}

function updateHandlePosition(ev: PointerEvent) {
  if (!dragging.value || !svg.value || !cArmPath.value) return;
  const { clientX, clientY } = ev;
  const svgBbox = svg.value.getBoundingClientRect();
  const svgX = clientX - svgBbox.left;
  const svgY = clientY - svgBbox.top;
  const percent = percentAlongGaugeArc(svgX, svgY);
  drawCArmMarker(percent);
  percentModel.value = percent;
}

function startDrag(ev: PointerEvent) {
  dragging.value = true;
  updateHandlePosition(ev);
}

function endDrag() {
  dragging.value = false;
}

useEventListener(window, 'pointermove', updateHandlePosition);
useEventListener(window, 'pointerup', endDrag);

onMounted(() => {
  drawCArmMarker(percentModel.value);
});
</script>

<template>
  <svg :height="size" :width="size" ref="svg">
    <path
      ref="cArmPath"
      :d="`M ${Mx} ${My} a ${radius} ${radius} 0 1 1 ${gap} 0`"
      fill="transparent"
      stroke="gray"
      stroke-width="10"
      @pointerdown="startDrag"
      class="path"
    />
    <circle
      :cx="handleX"
      :cy="handleY"
      r="10"
      fill="red"
      stroke="red"
      @pointerdown="startDrag"
      class="handle"
    ></circle>
  </svg>
</template>

<style type="text/css" scoped>
.handle {
  cursor: move;
}

.path {
  cursor: pointer;
}
</style>
