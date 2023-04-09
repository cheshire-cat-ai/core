import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchLanguageModels, setSelectedLLMProvider, updateLanguageModelSettings } from '@store/llmProviders/slice'
import { type AppDispatch } from '@store/index'
import {
  selectAllAvailableProviders,
  selectCurrentLLMProvider,
  selectCurrentProviderSchema,
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
  const error = useSelector(selectLLMProvidersError)
  const dispatch = useDispatch<AppDispatch>()

  const requireProviders = useCallback(() => {
    return dispatch(fetchLanguageModels())
  }, [dispatch])

  const selectProvider = useCallback((providerId: string) => {
    dispatch(setSelectedLLMProvider(providerId))
  }, [dispatch])

  const updateProviderSettings = useCallback((settings: LLMSettings) => {
    if (settings && selected) {
      return dispatch(updateLanguageModelSettings({ name: selected, settings }))
    }
  }, [dispatch, selected])

  return {
    isLoading,
    providers,
    schema,
    error,
    selected,
    updateProviderSettings,
    requireProviders,
    selectProvider
  }
}

export default useLLMProviders
