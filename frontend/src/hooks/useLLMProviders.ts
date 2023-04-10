import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  fetchLanguageModels,
  setLLMSettings,
  setSelectedLLMProvider,
  updateLanguageModelSettings
} from '@store/llmProviders/slice'
import { type AppDispatch } from '@store/index'
import {
  selectAllAvailableProviders,
  selectCurrentLLMProvider,
  selectCurrentProviderSchema,
  selectCurrentProviderSettings,
  selectLLMProvidersError,
  selectLLMProvidersIsLoading
} from '@store/llmProviders/selector'
import { type LLMSettings } from '@models/LLMSettings'

/**
 * A custom hook that returns the LLM providers state and a function to fetch the LLM providers.
 */
const useLLMProviders = () => {
  const selected = useSelector(selectCurrentLLMProvider)
  const isLoading = useSelector(selectLLMProvidersIsLoading)
  const providers = useSelector(selectAllAvailableProviders)
  const schema = useSelector(selectCurrentProviderSchema)
  const settings = useSelector(selectCurrentProviderSettings)
  const error = useSelector(selectLLMProvidersError)
  const dispatch = useDispatch<AppDispatch>()

  const requireProviders = useCallback(() => {
    return dispatch(fetchLanguageModels())
  }, [dispatch])

  const selectProvider = useCallback((providerId: string) => {
    dispatch(setSelectedLLMProvider(providerId))
  }, [dispatch])

  const updateProviderSettings = useCallback(() => {
    if (settings && selected) {
      return dispatch(updateLanguageModelSettings({ name: selected, settings }))
    }
  }, [dispatch, selected, settings])

  const setCurrentProviderSettings = useCallback((nextSettings: LLMSettings) => {
    if (nextSettings && selected) {
      return dispatch(setLLMSettings({ name: selected, settings: nextSettings }))
    }
  }, [dispatch, selected])

  return {
    isLoading,
    providers,
    schema,
    error,
    selected,
    settings,
    updateProviderSettings,
    requireProviders,
    selectProvider,
    setCurrentProviderSettings
  }
}

export default useLLMProviders
