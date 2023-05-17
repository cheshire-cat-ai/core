import type { PluginsState } from '@stores/types'
import type { Plugin } from '@models/Plugin'
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

  const togglePlugin = (id: Plugin['id']) => {
    console.log("Toggled", id)
  }
  
  return {
    currentState,
    togglePlugin
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePlugins, import.meta.hot))
}