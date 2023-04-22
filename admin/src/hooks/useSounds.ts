import { AppDispatch } from "@store/index"
import { selectSoundState } from "@store/soundControls/selectors"
import { toggleSounds } from "@store/soundControls/slice"
import { useCallback } from "react"
import { useDispatch, useSelector } from "react-redux"



const useSounds = () => {
    const volumeEnabled = useSelector(selectSoundState)
    const dispatch = useDispatch<AppDispatch>()

    const volumeController = useCallback(() => {
        return dispatch(toggleSounds())
    }, [dispatch])

    return { volumeEnabled, volumeController }
}

export default useSounds