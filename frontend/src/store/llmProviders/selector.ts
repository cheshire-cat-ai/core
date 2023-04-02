import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'

/**
 * Selects the root state for the llmProviders slice.
 */
const selectRootState = (state: RootState) => state.llmProviders

/**
 * Selects the 'loading' flag from the llmProviders state reporting whether a file is currently being uploaded.
 */
export const selectLLMProvidersIsLoading = createSelector(selectRootState, (state) => state.loading)

/**
 * Selects the error state from the llmProviders slice.
 * It contains the error message if an error occurred while sending a file.
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
