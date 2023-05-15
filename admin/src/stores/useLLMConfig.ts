import type { LLMConfigState } from '@stores/types'
import type { LLMConfigMetaData } from '@models/LLMConfig'
import LLMConfigService from '@services/LLMConfigService'
import { uniqueId } from '@utils/commons'
import { useNotifications } from '@stores/useNotifications'
import type { JSONSettings } from '@models/JSONSchema'

export const useLLMConfig = defineStore('llmProviders', () => {
  const currentState = reactive<LLMConfigState>({
    loading: false,
    settings: {}
  })

  const { showNotification } = useNotifications()

  const { state: providers, isLoading, error } = useAsyncState(LLMConfigService.getProviders(), undefined)

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
    if (!selected) return {} satisfies JSONSettings
    return currentState.settings[selected] ?? {} satisfies JSONSettings
  }

  const setLLMSettings = async (name: LLMConfigMetaData['languageModelName'], settings: JSONSettings) => {
    const result = await LLMConfigService.setProviderSettings(name, settings)
    showNotification({
      id: uniqueId(),
      type: result.status,
      message: result.message
    })
    if (result.status != 'error') {
      currentState.selected = name
      currentState.settings[name] = settings
    }
    return result.status != 'error'
  }

  return {
    currentState,
    setLLMSettings,
    getAvailableProviders,
    getProviderSchema,
    getProviderSettings
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useLLMConfig, import.meta.hot))
}