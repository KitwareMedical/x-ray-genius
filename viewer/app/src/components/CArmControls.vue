<script setup lang="ts">
import CArmDial from './CArmDial.vue';
import useCArmStore from '../store/c-arm';
import { computed } from 'vue';
import useViewAnimationStore from '@/src/store/view-animation';
import { useEventListener } from '@vueuse/core';
import { postCArmParameters } from '../api';
import { useLoadingState } from '../utils/useLoadingState';

const store = useCArmStore();
const tilt = computed({
  get: () => store.tilt,
  set: (v) => {
    store.setTilt(v);
  },
});
const tiltKappa = computed({
  get: () => store.tiltKappa,
  set: (v) => {
    store.setTiltKappa(v);
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
const dialPosition = computed({
  get: () => store.rotation,
  set: (v) => {
    store.setRotation(v);
  },
});
const rotationKappa = computed({
  get: () => store.rotationKappa,
  set: (v) => {
    store.setRotationKappa(v);
  },
});
const numberOfSamples = computed({
  get: () => store.numberOfSamples,
  set: (v) => {
    store.setNumberOfSamples(v);
  },
});

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
    .wrapPromise(postCArmParameters(store.toApiParameters()))
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
  <div class="controls">
    <c-arm-dial
      v-model="dialPosition"
      :size="200"
      @start-drag="startDrag"
      @end-drag="endDrag"
      :disabled="store.randomizeRotation"
    ></c-arm-dial>
    <div>{{ (dialPosition * 100).toFixed(0) }}%</div>
    <v-row>
      <v-col cols="3">
        <v-label class="mr-5"> Rotation <br />Concentration </v-label>
      </v-col>
      <v-col cols="3">
        <v-text-field
          v-model="rotationKappa"
          outlined
          type="number"
        ></v-text-field>
      </v-col>
      <v-col cols="6">
        <v-checkbox v-model="store.randomizeRotation">
          <template v-slot:label>
            <span class="mr-2">Randomize rotation (alpha)</span>
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
      </v-col>
    </v-row>
    <v-slider
      v-model="xTranslation"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      class="mt-5"
      label="X Translation"
      @pointerdown="startDrag"
    ></v-slider>
    <v-slider
      v-model="yTranslation"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      label="Y Translation"
      @pointerdown="startDrag"
    ></v-slider>
    <v-slider
      v-model="zTranslation"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      label="Z Translation"
      @pointerdown="startDrag"
    ></v-slider>
    <v-slider
      v-model="tilt"
      :disabled="store.randomizeTilt"
      min="0"
      max="1"
      step="0.01"
      style="width: 80%"
      label="Tilt"
      @pointerdown="startDrag"
    ></v-slider>
    <v-row>
      <v-col cols="3">
        <v-label class="mr-5"> Tilt <br />Concentration </v-label>
      </v-col>
      <v-col cols="3">
        <v-text-field v-model="tiltKappa" outlined type="number"></v-text-field>
      </v-col>
      <v-col cols="6">
        <v-checkbox v-model="store.randomizeTilt" label="Randomize tilt (beta)">
          <template v-slot:label>
            <span class="mr-2">Randomize tilt (beta)</span>
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
      </v-col>
    </v-row>
    <v-alert v-if="submissionError" color="error" class="mb-3">
      <div class="d-flex flex-row align-center">
        <v-icon class="mr-2">mdi-alert</v-icon>
        <span>Failed to submit session to the server</span>
      </div>
    </v-alert>
    <v-row>
      <v-col cols="6">
        <v-label>
          Number of
          <br />
          Samples
        </v-label>
      </v-col>
      <v-col cols="6">
        <v-text-field v-model="numberOfSamples" outlined></v-text-field>
      </v-col>
    </v-row>
    <v-btn :loading="submissionLoading" @click="submit">Submit</v-btn>
  </div>
</template>

<style type="text/css" scoped>
.controls {
  display: flex;
  flex-flow: column;
  align-items: center;
}
</style>
