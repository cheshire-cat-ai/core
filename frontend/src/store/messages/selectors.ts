import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'

/**
 * Selects the root state for the messages slice.
 */
const selectRootState = (state: RootState) => state.messages

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

/**
 * Selects 5 random default messages from the messages slice.
 */
export const selectRandomDefaultMessages = createSelector(selectRootState, (state) => {
  const defaultMessages = state.defaultMessages
  const messages = [...defaultMessages]
  const shuffled = messages.sort(() => 0.5 - Math.random())
  return shuffled.slice(0, 5)
})
