<template>
  <v-app>
    <app-bar @click:left-menu="leftSideBar = !leftSideBar"></app-bar>
    <v-navigation-drawer
      v-model="leftSideBar"
      app
      clipped
      touchless
      width="450"
      id="left-nav"
    >
      <module-panel @close="leftSideBar = false" />
    </v-navigation-drawer>
    <v-main id="content-main">
      <div class="fill-height d-flex flex-row flex-grow-1">
        <div class="d-flex flex-column flex-grow-1">
          <layout-grid v-show="hasData" :layout="layout" />
          <welcome-page
            v-if="!hasData"
            :loading="showLoading"
            class="clickable"
          >
          </welcome-page>
        </div>
      </div>
      <v-dialog :model-value="!!showError" width="35%" persistent>
        <v-card>
          <v-alert type="error" class="text-subtitle-1">
            <p>Failed to load data.</p>
            <p>Reason: {{ showError }}</p>
            <p>
              Please refresh to try again, or contact us to resolve the issue.
            </p>
          </v-alert>
        </v-card>
      </v-dialog>
    </v-main>
    <keyboard-shortcuts />
  </v-app>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { UrlParams } from '@vueuse/core';
import vtkURLExtract from '@kitware/vtk.js/Common/Core/URLExtract';
import { useDisplay } from 'vuetify';
import { useViewStore } from '@/src/store/views';
import useRemoteSaveStateStore from '@/src/store/remote-save-state';
import AppBar from '@/src/components/AppBar.vue';
import {
  loadFiles,
  loadUserPromptedFiles,
  loadUrls,
} from '@/src/actions/loadUserFiles';
import { useDICOMStore } from '@/src/store/datasets-dicom';
import LayoutGrid from '@/src/components/LayoutGrid.vue';
import DragAndDrop from '@/src/components/DragAndDrop.vue';
import PersistentOverlay from '@/src/components/PersistentOverlay.vue';
import KeyboardShortcuts from '@/src/components/KeyboardShortcuts.vue';
import { useImageStore } from '@/src/store/datasets-images';
import { useServerStore } from '@/src/store/server';
import { useGlobalErrorHook } from '@/src/composables/useGlobalErrorHook';
import { useKeyboardShortcuts } from '@/src/composables/useKeyboardShortcuts';
import { Layouts } from '@/src/config';
import { DefaultLayoutName } from '../config';
import { ImageMetadata } from '@/src/types/image';
import { mat3, vec3 } from 'gl-matrix';
import { Vector3 } from '@kitware/vtk.js/types';
import { onImageAdded } from '../composables/onImageAdded';

import useLoadDataStore from '../store/load-data';
import WelcomePage from './WelcomePage.vue';
import ModulePanel from './ModulePanel.vue';

export default defineComponent({
  name: 'App',

  components: {
    LayoutGrid,
    DragAndDrop,
    ModulePanel,
    PersistentOverlay,
    KeyboardShortcuts,
    WelcomePage,
    AppBar,
  },

  setup() {
    const imageStore = useImageStore();
    const dicomStore = useDICOMStore();

    useGlobalErrorHook();
    useKeyboardShortcuts();

    // --- file handling --- //

    const loadDataStore = useLoadDataStore();
    const hasData = computed(
      () =>
        imageStore.idList.length > 0 ||
        Object.keys(dicomStore.volumeInfo).length > 0
    );
    // show loading if actually loading or has any data,
    // since the welcome screen shouldn't be visible when
    // a dataset is opened.
    const showLoading = computed(
      () => loadDataStore.isLoading || hasData.value
    );
    const showError = ref<string | null>(null);

    // --- parse URL -- //

    const urlParams = vtkURLExtract.extractURLParameters() as UrlParams;

    onMounted(() => {
      if (!urlParams.urls) {
        return;
      }

      loadUrls(urlParams).then(([succeeded, errored]) => {
        if (!succeeded.length && errored.length) {
          showError.value = errored[0].errors[0].message;
        }
        console.log(showError.value);
      });
    });

    // --- remote server --- //

    const serverStore = useServerStore();

    onMounted(() => {
      serverStore.connect();
    });

    // --- save state --- //

    const remoteSaveStateStore = useRemoteSaveStateStore();
    if (import.meta.env.VITE_ENABLE_REMOTE_SAVE && urlParams.save) {
      remoteSaveStateStore.setSaveUrl(urlParams.save.toString());
    }

    // --- layout --- //

    const { layout } = storeToRefs(useViewStore());

    // --- //

    const viewStore = useViewStore();
    viewStore.setLayout(Layouts[DefaultLayoutName]);

    /**
     * Gets the basis vector flip factors when compared to LPS.
     */
    function getFlipFactors(metadata: ImageMetadata) {
      const { orientation, lpsOrientation } = metadata;
      const { Left, Posterior, Superior, Coronal, Sagittal, Axial } =
        lpsOrientation;
      const sVec = orientation.slice(Sagittal * 3, Sagittal * 3 + 3) as vec3;
      const cVec = orientation.slice(Coronal * 3, Coronal * 3 + 3) as vec3;
      const aVec = orientation.slice(Axial * 3, Axial * 3 + 3) as vec3;
      return [
        Math.sign(vec3.dot(sVec, Left)),
        Math.sign(vec3.dot(cVec, Posterior)),
        Math.sign(vec3.dot(aVec, Superior)),
      ] as Vector3;
    }

    // re-orient image to be supine and centered at the origin
    onImageAdded((id) => {
      const store = useImageStore();
      const image = store.dataIndex[id];
      const metadata = store.metadata[id];

      const dims = image.getDimensions();
      const spacing = image.getSpacing();
      const flipFactors = getFlipFactors(metadata);
      image.setOrigin(
        dims.map((d, i) => (-flipFactors[i] * (d * spacing[i])) / 2) as Vector3
      );

      const { lpsOrientation } = metadata;
      const transform = [
        ...lpsOrientation.Left,
        ...lpsOrientation.Posterior,
        ...lpsOrientation.Superior,
      ] as mat3;
      mat3.invert(transform, transform);

      const orientation = mat3.create();
      mat3.mul(orientation, transform, image.getDirection());
      image.setDirection(orientation);

      image.computeTransforms();
      store.updateData(id, image);
    });

    const display = useDisplay();

    return {
      leftSideBar: ref(!display.mobile.value),
      loadUserPromptedFiles,
      loadFiles,
      hasData,
      showLoading,
      showError,
      layout,
    };
  },
});
</script>

<style>
#content-main {
  /* disable v-content transition when we resize our app drawer */
  transition: initial;
  width: 100%;
  height: 100%;
  position: fixed;
}

#left-nav {
  border-right: 1px solid rgb(var(--v-theme-background));
}

#content-main > .v-content__wrap {
  display: flex;
}

#module-switcher .v-input__prepend-inner {
  /* better icon alignment */
  margin-top: 15px;
}

.alert > .v-snack__wrapper {
  /* transition background color */
  transition: background-color 0.25s;
}
</style>

<style src="@/src/components/styles/utils.css"></style>

<style scoped>
#app-container {
  width: 100%;
  height: 100%;
}

.dnd-prompt {
  background: rgba(0, 0, 0, 0.4);
  color: white;
  border-radius: 8px;
  box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.4);
  padding: 64px;
}
</style>
