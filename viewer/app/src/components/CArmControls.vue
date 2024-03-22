<script setup lang="ts">
import CArmDial from './CArmDial.vue';
import useCArmStore, { useCArmPhysicalParameters } from '../store/c-arm';
import { computed } from 'vue';
import useViewAnimationStore from '@/src/store/view-animation';
import { useEventListener } from '@vueuse/core';
import { exportApiParameters, postCArmParameters } from '../api';
import { useLoadingState } from '../utils/useLoadingState';
import { useCurrentImage } from '@/src/composables/useCurrentImage';

const store = useCArmStore();
const tilt = computed({
  get: () => store.tilt,
  set: (v) => {
    store.setTilt(v);
  },
});
const tiltKappaStdDev = computed({
  get: () => store.tiltKappaStdDev,
  set: (v) => {
    store.setTiltKappaStdDev(v);
  },
});
const xTranslation = computed({
  get: () => store.translation[0],
  set: (v) => {
    store.setXTranslation(v);
  },
});
const yTranslation = computed({
  get: () => store.translation[1],
  set: (v) => {
    store.setYTranslation(v);
  },
});
const zTranslation = computed({
  get: () => store.translation[2],
  set: (v) => {
    store.setZTranslation(v);
  },
});
const rotation = computed({
  get: () => store.rotation,
  set: (v) => {
    store.setRotation(v);
  },
});
const rotationKappaStdDev = computed({
  get: () => store.rotationKappaStdDev,
  set: (v) => {
    store.setRotationKappaStdDev(v);
  },
});
const numberOfSamples = computed({
  get: () => store.numberOfSamples,
  set: (v) => {
    store.setNumberOfSamples(v);
  },
});

const { currentImageID } = useCurrentImage();
const {
  armTranslation: physicalTranslation,
  armRotationDeg,
  armTiltDeg,
} = useCArmPhysicalParameters(currentImageID);

const viewAnimationStore = useViewAnimationStore();
const animationKey = Symbol('CArmControls');

const startDrag = () => {
  viewAnimationStore.requestAnimation(animationKey);
};

const endDrag = () => {
  viewAnimationStore.cancelAnimation(animationKey);
};

useEventListener(window, 'pointerup', endDrag);

const submission = useLoadingState();
const { loading: submissionLoading, error: submissionError } = submission;

async function submit() {
  submission
    .wrapPromise(postCArmParameters(exportApiParameters()))
    .then(() => {
      window.location.pathname =
        import.meta.env.VITE_SUBMISSION_REDIRECT ?? '/';
    })
    .catch(() => {
      // noop
    });
}
</script>

<template>
  <div class="controls mt-3">
    <div class="w-100 px-3">
      <span class="text-subtitle-2">Rotation &amp; Tilt</span>
      <v-divider height="2px" />
      <v-row>
        <v-col cols="6">
          <c-arm-dial
            v-model="rotation"
            :size="200"
            @start-drag="startDrag"
            @end-drag="endDrag"
            :disabled="store.randomizeRotation"
          ></c-arm-dial>
          <div class="text-center label mt-n8 d-flex flex-column align-center">
            <div>{{ armRotationDeg.toFixed(2) }}˚</div>
            <div>Rotation (Rainbow)</div>
          </div>
          <v-checkbox v-model="store.randomizeRotation" class="mt-3">
            <template v-slot:label>
              <span class="mr-2">Randomize Rotation (alpha)</span>
              <v-tooltip bottom>
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" class="help-icon">
                    mdi-help-circle-outline
                  </v-icon>
                </template>
                <p>
                  Checking this box will randomize the rotation of the C-Arm on
                  each batch
                  <br />
                  generation instead of fixing it to a constant value.
                </p>
              </v-tooltip>
            </template>
          </v-checkbox>
          <v-text-field
            v-model="rotationKappaStdDev"
            outlined
            type="number"
            step="0.1"
            label="Rotation Conc. Std Dev"
            suffix="deg"
          ></v-text-field>
        </v-col>
        <v-col cols="6">
          <c-arm-dial
            v-model="tilt"
            :size="200"
            @start-drag="startDrag"
            @end-drag="endDrag"
            :disabled="store.randomizeTilt"
          ></c-arm-dial>
          <div class="text-center label mt-n8 d-flex flex-column align-center">
            <div>{{ armTiltDeg.toFixed(2) }}˚</div>
            <div>Tilt (Head/Foot)</div>
          </div>
          <v-checkbox v-model="store.randomizeTilt" class="mt-3">
            <template v-slot:label>
              <span class="mr-2">Randomize Tilt</span>
              <v-tooltip bottom>
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" class="help-icon">
                    mdi-help-circle-outline
                  </v-icon>
                </template>
                <p>
                  Checking this box will randomize the tilt of the C-Arm on each
                  batch
                  <br />
                  generation instead of fixing it to a constant value.
                </p>
              </v-tooltip>
            </template>
          </v-checkbox>
          <v-text-field
            v-model="tiltKappaStdDev"
            outlined
            type="number"
            step="0.1"
            label="Tilt Concentration Std Dev"
            suffix="deg"
          ></v-text-field>
        </v-col>
      </v-row>
    </div>
    <div class="w-100 px-3">
      <span class="text-subtitle-2">Translation</span>
      <v-divider height="2px" />
      <v-slider
        v-model="xTranslation"
        min="-0.5"
        max="0.5"
        step="0.001"
        class="mt-5"
        hide-details
        density="compact"
        :disabled="!currentImageID"
        @pointerdown="startDrag"
      >
        <template #label>
          <v-label class="d-flex flex-column align-center">
            <div>Left/Right</div>
            <div>{{ (physicalTranslation[0] / 10).toFixed(1) }} cm</div>
          </v-label>
        </template>
        <template #append>
          <div class="d-flex flex-column" @pointerdown.stop>
            <v-checkbox
              v-model="store.randomizeX"
              hide-details
              label="Randomize"
            ></v-checkbox>
            <v-text-field
              v-if="store.randomizeX"
              v-model="store.randStdDevX"
              label="Std Dev (mm)"
              type="number"
              density="compact"
              hide-details
              variant="outlined"
              class="std-dev-editor"
            ></v-text-field>
          </div>
        </template>
      </v-slider>
      <v-slider
        v-model="yTranslation"
        min="-0.5"
        max="0.5"
        step="0.001"
        hide-details
        density="compact"
        :disabled="!currentImageID"
        @pointerdown="startDrag"
      >
        <template #label>
          <v-label class="d-flex flex-column align-center">
            <div>Up/Down</div>
            <div>{{ (physicalTranslation[1] / 10).toFixed(1) }} cm</div>
          </v-label>
        </template>
        <template #append>
          <div class="d-flex flex-column" @pointerdown.stop>
            <v-checkbox
              v-model="store.randomizeY"
              hide-details
              label="Randomize"
            ></v-checkbox>
            <v-text-field
              v-if="store.randomizeY"
              v-model="store.randStdDevY"
              label="Std Dev (mm)"
              type="number"
              density="compact"
              hide-details
              variant="outlined"
              class="std-dev-editor"
            ></v-text-field>
          </div>
        </template>
      </v-slider>
      <v-slider
        v-model="zTranslation"
        min="-0.5"
        max="0.5"
        step="0.001"
        hide-details
        density="compact"
        :disabled="!currentImageID"
        @pointerdown="startDrag"
      >
        <template #label>
          <v-label class="d-flex flex-column align-center">
            <div>Foot/Head</div>
            <div>{{ (physicalTranslation[2] / 10).toFixed(1) }} cm</div>
          </v-label>
        </template>
        <template #append>
          <div class="d-flex flex-column" @pointerdown.stop>
            <v-checkbox
              v-model="store.randomizeZ"
              hide-details
              label="Randomize"
            ></v-checkbox>
            <v-text-field
              v-if="store.randomizeZ"
              v-model="store.randStdDevZ"
              label="Std Dev (mm)"
              type="number"
              density="compact"
              hide-details
              variant="outlined"
              class="std-dev-editor"
            ></v-text-field>
          </div>
        </template>
      </v-slider>
    </div>
    <div class="w-100 px-3 d-flex flex-column">
      <v-divider class="pb-5" height="2px" />
      <v-alert v-if="submissionError" color="error" class="mb-3">
        <div class="d-flex flex-row align-center">
          <v-icon class="mr-2">mdi-alert</v-icon>
          <span>Failed to submit session to the server</span>
        </div>
      </v-alert>
      <v-text-field
        label="Number of Samples"
        v-model="numberOfSamples"
        outlined
      ></v-text-field>
      <v-btn
        variant="tonal"
        color="secondary"
        :loading="submissionLoading"
        @click="submit"
        >Submit</v-btn
      >
    </div>
  </div>
</template>

<style type="text/css" scoped>
.controls {
  display: flex;
  flex-flow: column;
  align-items: center;
}

.label {
  opacity: var(--v-medium-emphasis-opacity);
}

.std-dev-editor {
  width: min-content;
  min-width: 100%;
}
</style>
