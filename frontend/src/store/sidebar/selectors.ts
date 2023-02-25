import { createSelector } from '@reduxjs/toolkit'
import { type RootState } from '../'

const selectRootState = (state: RootState) => state.faqs

export const selectFAQs = createSelector([selectRootState], ({ data }) => data)
