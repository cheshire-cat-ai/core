import type { PluginsState } from '@stores/types'
import PluginsService from '@services/PluginsService'

export const usePlugins = defineStore('plugins', () => {
  const currentState = reactive<PluginsState>({
    loading: false,
    data: []
  })

  const { state: plugins, isLoading, error } = useAsyncState(PluginsService.getPlugins(), undefined)

  watchEffect(() => {
    currentState.loading = isLoading.value
    currentState.data = plugins.value ?? []
    currentState.error = error.value as string
  })

  return {
    currentState
  }
})