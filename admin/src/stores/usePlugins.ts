import type { PluginsState } from '@stores/types'
import PluginService from '@services/PluginService'

export const usePlugins = defineStore('plugins', () => {
  const currentState = reactive<PluginsState>({
    loading: false,
    data: []
  })

  const { state: plugins, isLoading, error } = useAsyncState(PluginService.getPlugins(), [])

  watchEffect(() => {
    currentState.loading = isLoading.value
    currentState.data = plugins.value
    currentState.error = error.value as string
  })

  return {
    currentState
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePlugins, import.meta.hot))
}