<script setup>
import { ref } from 'vue';
import { useDisplay } from 'vuetify';
import VolViewFullLogo from './icons/VolViewFullLogo.vue';
import VolViewLogo from '@/src/components/icons/VolViewLogo.vue';

const emit = defineEmits(['click:left-menu']);

const { mobile } = useDisplay();
const aboutBoxDialog = ref(false);
</script>

<template>
  <v-app-bar app clipped-left :height="48">
    <v-btn v-if="mobile" icon="mdi-menu" @click="emit('click:left-menu')" />
    <v-toolbar-title class="d-flex flex-row align-center mt-3">
      <vol-view-logo v-if="mobile" />
      <vol-view-full-logo v-else />
    </v-toolbar-title>
    <v-btn
      variant="text"
      icon
      :rounded="0"
      class="toolbar-button"
      href="/contact/"
      target="_blank"
    >
      <v-icon icon="mdi-forum"></v-icon>
      <v-tooltip activator="parent" location="bottom">Contact Us</v-tooltip>
    </v-btn>
    <v-btn
      variant="text"
      icon
      :rounded="0"
      class="toolbar-button"
      href="/faq/"
      target="_blank"
    >
      <v-icon icon="mdi-help-circle-outline"></v-icon>
      <v-tooltip activator="parent" location="bottom">FAQ</v-tooltip>
    </v-btn>
  </v-app-bar>
</template>

<style src="@/src/components/styles/utils.css"></style>
<style scoped>
.toolbar-button {
  min-height: 100%; /* fill toolbar height */
}
</style>
