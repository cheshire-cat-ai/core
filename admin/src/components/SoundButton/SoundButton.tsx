import { Button } from "antd";
import { FC } from "react";
import VolumeEnabled from './volume-high-solid.svg'
import VolumeDisabled from './volume-xmark-solid.svg'
import useToggle from "beautiful-react-hooks/useToggle";
import clsx from "clsx";
import style from './SoundButton.module.scss'
import { useDispatch, useSelector } from "react-redux";
import { toggleSounds } from '@store/soundControls/slice'
import { selectSoundState } from "@store/soundControls/selectors";

/**
 * this is a button to mute or unmute the sound
 *  
 */

const SoundButton: FC = () => {
    const volumeEnabled = useSelector(selectSoundState)
    const dispatch = useDispatch()
    
    const volumeController = () => {
        dispatch(toggleSounds())
    }

    return (
        <div>
            <Button onClick={volumeController} icon={volumeEnabled ? <VolumeEnabled /> : <VolumeDisabled />} className={clsx(style.soundBtn)} />
        </div>
    )
}
export default SoundButton
