import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'

/**
 * Selects the root state for the fileUploader slice.
 */
const selectRootState = (state: RootState) => state.fileUploader

/**
 * Selects the 'loading' flag from the fileUploader state reporting whether a file is currently being uploaded.
 */
export const selectFileUploadIsLoading = createSelector(selectRootState, (state) => state.loading)

/**
 * Selects the error state from the fileUploader slice.
 * It contains the error message if an error occurred while sending a file.
 */
export const selectFileUploadError = createSelector(selectRootState, (state) => state.error)

/**
 * Selects the response from the fileUploader slice.
 */
export const selectFileUploadResponse = createSelector(selectRootState, (state) => state.data)
