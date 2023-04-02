import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchLanguageModels, setSelectedLLMProvider } from '@store/llmProviders/slice'
import { type AppDispatch } from '@store/index'
import {
  selectCurrentLLMProvider,
  selectLLMProvidersError,
  selectLLMProvidersIsLoading,
  selectLLMProvidersResponse
} from '@store/llmProviders/selector'
import { type LLMProviderDescriptor } from '@models/LLMProviderDescriptor'

/**
 * A custom hook that returns the LLM providers state and a function to fetch the LLM providers.
 */
const useLLMProviders = () => {
  const selected = useSelector(selectCurrentLLMProvider)
  const isLoading = useSelector(selectLLMProvidersIsLoading)
  const providers = useSelector(selectLLMProvidersResponse)
  const error = useSelector(selectLLMProvidersError)
  const dispatch = useDispatch<AppDispatch>()

  const requireLLMProviders = useCallback(() => {
    void dispatch(fetchLanguageModels())
  }, [dispatch])

  const selectLLMProvider = useCallback((providerId: LLMProviderDescriptor['id']) => {
    dispatch(setSelectedLLMProvider(providerId))
  }, [dispatch])

  return {
    isLoading,
    providers,
    error,
    selected,
    requireLLMProviders,
    selectLLMProvider
  }
}

export default useLLMProviders
