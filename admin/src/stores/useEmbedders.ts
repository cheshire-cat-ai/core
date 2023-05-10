import type { JSONSettings } from '@models/JSONSchema'
import EmbedderService from '@services/EmbedderService'
import type { EmbeddersState } from '@stores/types'

export const useEmbedders = defineStore('embedder', () => {

  const currentState = reactive<EmbeddersState>({
    loading: false,
    updating: false,
    settings: {},
  })

  const { state: embedders, isLoading, error } = useAsyncState(EmbedderService.getEmbedders(), undefined)

  watchEffect(() => {
    currentState.loading = isLoading.value
    currentState.data = embedders.value
    currentState.error = error.value as string
  })

  const getEmbedderSchema = (selected = currentState.selected) => {
    if (!selected) return undefined
    return getAvailableEmbedders().find((schema) => schema.languageEmbedderName === selected)
  }

  const getEmbedderSettings = (selected = currentState.selected) => {
    if (!selected) return {} satisfies JSONSettings
    return currentState.settings[selected] ?? {} satisfies JSONSettings
  }

  const getAvailableEmbedders = () => {
    return embedders.value?.schemas ? Object.values(embedders.value.schemas) : []
  }

  return {
    currentState,
    getAvailableEmbedders,
    getEmbedderSchema,
    getEmbedderSettings
  }
})