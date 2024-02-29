import { computed, ref } from 'vue';

export function useLoadingState() {
  const loading = ref(false);
  const error = ref<unknown>();
  const isErrorSet = computed(() => error.value !== undefined);
  const wrapPromise = (
    promise: Promise<any>,
    suppressError: boolean = false
  ) => {
    error.value = undefined;
    loading.value = true;
    promise
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    if (suppressError)
      return promise.catch(() => {
        /*noop*/
      });
    return promise;
  };
  return { loading, error, isErrorSet, wrapPromise };
}
