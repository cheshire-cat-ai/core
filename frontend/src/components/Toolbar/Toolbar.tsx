import React, { type FC, type ReactElement } from 'react'
import clsx from 'clsx'
import SettingsIcon from './settings.svg'
import { type CommonProps, type ComponentRenderer } from '@models/commons'
import { handleReactElementOrRenderer } from '@utils/commons'

import style from './Toolbar.module.scss'

/**
 * Renders the header's toolbar component.
 */
const Toolbar: FC<ToolbarProps> = (props) => {
  const { title, ToolbarActions, onSettingsClick, className, ...rest } = props
  const classList = clsx(style.toolbar, className)

  return (
    <div className={classList} role="toolbar" {...rest}>
      <div className={style.title}>
        <h1>{title ?? '😸 Cheshire cat'}</h1>
      </div>
      <button role="button" onClick={onSettingsClick} disabled>
        {handleReactElementOrRenderer(ToolbarActions ?? SettingsIcon)}
      </button>
    </div>
  )
}

export interface ToolbarProps extends CommonProps {
  /**
   * The title to be displayed in the toolbar.
   */
  title?: string
  /**
   * The callback function to be invoked when the settings button is clicked.
   */
  onSettingsClick?: React.MouseEventHandler<HTMLButtonElement>
  /**
   * The component to be rendered as the toolbar's actions.
   */
  ToolbarActions?: ComponentRenderer | ReactElement
}

export default React.memo(Toolbar)
