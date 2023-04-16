import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'
import { type SettingsRecord } from '@models/JSONSchemaBasedSettings'

/**
 * Selects the root state for the languageModels slice.
 */
const selectRootState = (state: RootState) => state.languageModels

/**
 * Selects the 'loading' flag from the languageModels state reporting whether a file is currently being uploaded.
 */
export const selectLanguageModelsLoading = createSelector(selectRootState, (state) => state.loading)

/**
 * Selects the error state from the languageModels slice.
 * It contains the error message if an error occurred while sending a file.
 */
export const selectLanguageModelsError = createSelector(selectRootState, (state) => state.error)

/**
 * Selects the response from the languageModels slice.
 */
export const selectLanguageModelData = createSelector(selectRootState, (state) => state.data)

/**
 * Selects the selected languageModels from the languageModels slice.
 */
export const selectCurrentLanguageModel = createSelector(selectRootState, (state) => state.selected)

/**
 * Selects the list of all available language model from the languageModels slice.
 */
export const selectAllAvailableProviders = createSelector(selectLanguageModelData, (providers) => {
  return providers?.schemas ? Object.values(providers.schemas) : []
})

/**
 * Selects the schema for the current language model provider
 */
export const selectCurrentProviderSchema = createSelector(
  [selectAllAvailableProviders, selectCurrentLanguageModel],
  (schemas, selected) => {
    if (!selected) return undefined
    return schemas.find((schema) => schema.languageModelName === selected)
  }
)

/**
 * TODO: Write a better documentation here.
 */
export const selectAllLanguageModelsSettings = createSelector(selectRootState, (state) => state.settings)

/**
 * TODO: Write a better documentation here.
 */
export const selectCurrentLanguageModelSettings = createSelector(
  [selectAllLanguageModelsSettings, selectCurrentLanguageModel],
  (providers, current) => {
    if (!current) return {} satisfies SettingsRecord

    return providers[current] ?? {} satisfies SettingsRecord
  }
)
