import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'

/**
 * Selects the root state for the messages slice.
 * @param state
 */
const selectRootState = (state: RootState) => state.messages

/**
 * Selects the default messages from the messages slice.
 */
export const selectDefaultMessages = createSelector(selectRootState, (state) => state.defaultMessages)

/**
 * Selects the current messages from the messages slice.
 */
export const selectCurrentMessages = createSelector(selectRootState, (state) => state.messages)

/**
 * Selects the loading state from the messages slice.
 * It tells whether the app is currently sending a message.
 */
export const selectIsSendingMessage = createSelector(selectRootState, (state) => state.loading)
