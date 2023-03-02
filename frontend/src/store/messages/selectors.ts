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
 * Selects the ready state from the messages slice.
 * It tells whether the app is ready to send/receive messages.
 */
export const selectIsReady = createSelector(selectRootState, (state) => state.ready)

/**
 * Selects the loading state from the messages slice.
 * It tells whether the app is currently sending a message.
 */
export const selectIsSendingMessage = createSelector(selectRootState, (state) => state.loading)

/**
 * Selects the error state from the messages slice.
 * It contains the error message if an error occurred while sending a message.
 */
export const selectError = createSelector(selectRootState, (state) => state.error)
