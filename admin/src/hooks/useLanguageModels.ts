import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchLanguageModels, setSelectedLLMProvider } from '@store/languageModels/slice'
import { type AppDispatch } from '@store/index'
import {
  selectAllAvailableProviders,
  selectCurrentProviderSchema,
  selectLanguageModelsError,
  selectLanguageModelsLoading
} from '@store/languageModels/selector'

/**
 * A custom hook that returns the LLM providers state and a function to fetch the LLM providers.
 */
const useLanguageModels = () => {
  const dispatch = useDispatch<AppDispatch>()
  const isLoading = useSelector(selectLanguageModelsLoading)
  const providers = useSelector(selectAllAvailableProviders)
  const schema = useSelector(selectCurrentProviderSchema)
  const error = useSelector(selectLanguageModelsError)

  const requireProviders = useCallback(() => {
    return dispatch(fetchLanguageModels())
  }, [dispatch])

  const selectProvider = useCallback((providerId: string) => {
    dispatch(setSelectedLLMProvider(providerId))
  }, [dispatch])

  return {
    isLoading,
    providers,
    schema,
    error,
    requireProviders,
    selectProvider
  }
}

export default useLanguageModels
