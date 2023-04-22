import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'

/**
 * Selects the root state for the plugins slice.
 */
const selectRootState = (state: RootState) => state.plugins

/**
 * Selects the 'loading' flag from the plugins state reporting whether a plugin is currently being uploaded.
 */
export const selectPluginsIsLoading = createSelector(selectRootState, (state) => state.loading)

/**
 * Selects the error state from the plugins slice.
 * It contains the error message if an error occurred while getting plugins.
 */
export const selectPluginsError = createSelector(selectRootState, (state) => state.error)

/**
 * Selects all plugins from the plugins slice.
 */
export const selectAllPlugins = createSelector(selectRootState, (state) => state.data)
