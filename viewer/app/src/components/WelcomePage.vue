<script setup lang="ts">
import { ref, toRefs } from 'vue';
import { watchImmediate } from '@vueuse/core';

const props = withDefaults(
  defineProps<{
    loading?: boolean;
  }>(),
  {
    loading: false,
  }
);

const { loading } = toRefs(props);

function useTimedMessages(
  firstMessage: string,
  nextMessages: Array<{ message: string; delayMs: number }>
) {
  const currentMessage = ref(firstMessage);
  const running = ref(false);
  let timer: number = 0;

  const stop = () => {
    if (!running.value) return;
    running.value = false;
    clearTimeout(timer);
  };

  const runTimer = (idx: number) => {
    if (idx >= nextMessages.length) return;

    const nextMsg = nextMessages[idx];
    timer = setTimeout(() => {
      currentMessage.value = nextMsg.message;
      runTimer(idx + 1);
    }, nextMsg.delayMs) as unknown as number;
  };

  const restart = () => {
    stop();

    running.value = true;
    currentMessage.value = firstMessage;

    runTimer(0);
  };

  return { contents: currentMessage, restart, stop };
}

const timedMessage = useTimedMessages('Loading data...', [
  { message: 'Still loading your data...', delayMs: 5 * 1000 },
  { message: 'Just a little bit longer...', delayMs: 5 * 1000 },
  { message: 'A few more moments (slow download?)...', delayMs: 5 * 1000 },
  { message: 'Still working (likely a slow download)...', delayMs: 5 * 1000 },
]);

watchImmediate(loading, () => {
  if (loading.value) {
    timedMessage.restart();
  } else {
    timedMessage.stop();
  }
});

const { contents: loadingMesage } = timedMessage;
</script>

<template>
  <v-container class="page-container" v-bind="$attrs">
    <v-col>
      <v-row justify="center">
        <v-card
          flat
          dark
          rounded="0"
          color="transparent"
          class="text-center headline"
        >
          <template v-if="loading">
            <div class="text-h6 my-4">{{ loadingMesage }}</div>
            <v-progress-linear indeterminate />
          </template>
        </v-card>
      </v-row>
    </v-col>
  </v-container>
</template>

<style scoped>
.page-container {
  flex: 1 1 auto;
  display: flex;
  flex-flow: row;
  align-items: center;
  max-width: 100%;
}

.vertical-offset-margin {
  margin-top: 128px;
}
</style>
