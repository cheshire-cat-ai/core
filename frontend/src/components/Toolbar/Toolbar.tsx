import React, { type FC } from 'react'
import clsx from 'clsx'
import SettingsIcon from './settings.svg'
import { type CommonProps } from '@models/commons'

import style from './Toolbar.module.scss'

/**
 * Renders the header's toolbar component
 */
const Toolbar: FC<ToolbarProps> = ({ onSettingsClick, className, ...rest }) => (
  <div className={clsx(style.toolbar, className)} role="toolbar" {...rest}>
    <button role="button" onClick={onSettingsClick}>
      <SettingsIcon />
    </button>
  </div>
)

export interface ToolbarProps extends CommonProps {
  /**
   * The callback function to be invoked when the settings button is clicked.
   */
  onSettingsClick?: React.MouseEventHandler<HTMLButtonElement>
}

export default React.memo(Toolbar)
