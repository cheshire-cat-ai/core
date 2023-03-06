import React, { type FC } from 'react'
import clsx from 'clsx'
import SettingsIcon from './settings.svg'
import { type CommonProps } from '@models/commons'

import style from './Toolbar.module.scss'

/**
 * Renders the header's toolbar component.
 */
const Toolbar: FC<ToolbarProps> = ({ onSettingsClick, className, ...rest }) => (
  <div className={clsx(style.toolbar, className)} role="toolbar" {...rest}>
    <div className={style.title}>
      <h1>😸 Cheshire cat</h1>
    </div>
    <button role="button" onClick={onSettingsClick} disabled>
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
