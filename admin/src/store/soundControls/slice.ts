import { createSlice } from "@reduxjs/toolkit"

const initialState: boolean = true

const soundsSlice = createSlice({
    name: 'sounds',
    initialState,
    reducers: {
        toggleSounds(state) {
            state = !state
            return state
        }
    }
})

export const { toggleSounds } = soundsSlice.actions
export default soundsSlice.reducer