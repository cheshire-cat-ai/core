import { reactive, watchEffect } from 'vue'
import { defineStore } from 'pinia'
import type { LLMProvidersState } from '@stores/types'
import type { LLMProviderMetaData, LLMSettings } from '@models/LLMProvider'
import { useAsyncState } from '@vueuse/core'
import LanguageModels from '@services/LanguageModels'
import { uniqueId } from '@utils/commons'
import { useNotifications } from '@stores/useNotifications'

export const useLLMProviders = defineStore('llmProviders', () => {
  const currentState = reactive<LLMProvidersState>({
    loading: false,
    updating: false,
    settings: {}
  })

  const { showNotification } = useNotifications()

  const { state: providers, isLoading, error } = useAsyncState(LanguageModels.getProviders(), undefined)

  watchEffect(() => {
    currentState.loading = isLoading.value
    currentState.data = providers.value
    currentState.error = error.value as string
    if (currentState.data) {
      currentState.selected = currentState.data.selected_configuration ?? Object.values(currentState.data.schemas)[0].languageModelName
      currentState.settings = currentState.data.settings.reduce((acc, { name, value }) => ({ ...acc, [name]: value }), {})
    }
  })

  const getAvailableProviders = () => {
    return providers.value?.schemas ? Object.values(providers.value.schemas) : []
  }

  const getProviderSchema = (selected = currentState.selected) => {
    if (!selected) return undefined
    return getAvailableProviders().find((schema) => schema.languageModelName === selected)
  }

  const getProviderSettings = (selected = currentState.selected) => {
    if (!selected) return {} satisfies LLMSettings
    return currentState.settings[selected] ?? {} satisfies LLMSettings
  }

  const setLLMSettings = async (name: LLMProviderMetaData['languageModelName'], settings: LLMSettings) => {
    currentState.updating = true
    const result = await LanguageModels.setProviderOptions(name, settings)
    const isError = result instanceof Error
    showNotification({
      id: uniqueId(),
      type: isError ? 'error' : 'success',
      message: isError ? result.message : 'Language model provider updated'
    })
    currentState.updating = false
    if (!isError) {
      currentState.selected = name
      currentState.settings[name] = settings
    }
    return !isError
  }

  return {
    currentState,
    setLLMSettings,
    getAvailableProviders,
    getProviderSchema,
    getProviderSettings
  }
})