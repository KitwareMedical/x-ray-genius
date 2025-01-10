<template>
  <v-card class="container">
    <iframe ref="iframe" src="/faq-embedded" allowtransparency="true"></iframe>
    <div class="progress">
      <v-progress-circular indeterminate />
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

const iframe = ref<HTMLIFrameElement | null>();

onMounted(() => {
  iframe.value?.addEventListener('load', () => {
    if (!iframe.value) return;
    iframe.value.style.visibility = 'visible';
  });
});
</script>

<style scoped>
iframe {
  border: none;
  height: 100%;
  width: 100%;
  visibility: hidden;
  z-index: 10;
}

.container {
  position: relative;
  height: 80vh;
  display: flex;
  flex-flow: column;
  align-items: center;
}

.progress {
  position: absolute;
  top: 50%;
  margin: 0 auto;
  transform: translateY(-50%);
}
</style>
