import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'
import { type LLMSettings } from '@models/LLMSettings'

/**
 * Selects the root state for the llmProviders slice.
 */
const selectRootState = (state: RootState) => state.llmProviders

/**
 * Selects the 'loading' flag from the llmProviders state.
 */
export const selectLLMProvidersIsLoading = createSelector(selectRootState, (state) => state.loading)

/**
 * Selects the error state from the llmProviders slice.
 * It contains the error message if an error occurred while selecting LLM providers.
 */
export const selectLLMProvidersError = createSelector(selectRootState, (state) => state.error)

/**
 * Selects the response from the llmProviders slice.
 */
export const selectLLMProvidersResponse = createSelector(selectRootState, (state) => state.data)

/**
 * Selects the selected LLM provider from the llmProviders slice.
 */
export const selectCurrentLLMProvider = createSelector(selectRootState, (state) => state.selected)

/**
 * Selects the list of all available language model providers from the llmProviders slice.
 */
export const selectAllAvailableProviders = createSelector(selectLLMProvidersResponse, (providers) => {
  return providers?.schemas ? Object.values(providers.schemas) : []
})

/**
 * Selects the schema for the current language model provider
 */
export const selectCurrentProviderSchema = createSelector(
  [selectAllAvailableProviders, selectCurrentLLMProvider],
  (schemas, selected) => {
    if (!selected) return undefined
    return schemas.find((schema) => schema.languageModelName === selected)
  }
)

/**
 * Selects all language model providers
 */
export const selectAllLLMSettings = createSelector(selectRootState, (state) => state.settings)

/**
 * Selects the current language model provider settings form the `llmProviders` slice
 */
export const selectCurrentProviderSettings = createSelector(
  [selectAllLLMSettings, selectCurrentLLMProvider],
  (providers, current) => {
    if (!current) return {} satisfies LLMSettings

    return providers[current] ?? {} satisfies LLMSettings
  }
)
