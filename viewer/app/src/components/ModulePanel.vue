<template>
  <div class="fill-height d-flex flex-column">
    <div id="module-container">
      <c-arm-controls></c-arm-controls>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, defineComponent, ref } from 'vue';
import CArmControls from './CArmControls.vue';

interface Module {
  name: string;
  icon: string;
  component: Component;
}

const Modules: Module[] = [
  {
    name: 'Data',
    icon: 'database',
    component: CArmControls,
  },
];

export default defineComponent({
  name: 'ModulePanel',
  components: {
    CArmControls,
  },
  setup() {
    const selectedModuleIndex = ref(0);

    return {
      selectedModuleIndex,
      Modules,
    };
  },
});
</script>

<style scoped>
#module-switcher {
  display: relative;
  flex: 0 2;
  /* roughly match vuetify's dark/light transition */
  transition: border-bottom 0.3s;
  border-bottom: 2px solid rgb(var(--v-theme-on-surface-variant));
}

#close-btn {
  position: absolute;
  top: 1.5em;
  left: 0.5em;
  z-index: 10;
}

#module-container {
  position: relative;
  flex: 2;
  overflow: auto;
}

.module-text {
  font-size: 0.6rem;
  white-space: pre;
}

.tab-content {
  display: flex;
  justify-content: flex-end;
  flex-direction: column-reverse;
  height: 100%;
  align-items: center;
}

#module-switcher-tabs :deep(.v-slide-group__content) {
  justify-content: center;
}

#module-switcher-tabs
  :deep(.v-slide-group__prev.v-slide-group__prev--disabled) {
  visibility: hidden;
}

#module-switcher-tabs
  :deep(.v-slide-group__next.v-slide-group__next--disabled) {
  visibility: hidden;
}
</style>
