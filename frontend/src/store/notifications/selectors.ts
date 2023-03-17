import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '@store/index'

/**
 * Selects the root state for the 'notifications' slice.
 */
const selectRootState = (state: RootState) => state.notifications

/**
 * Selects the current notifications
 */
export const selectNotifications = createSelector(selectRootState, (state) => {
  return state.history.filter((notification) => !notification.hidden)
})
