import React, { type FC, type PropsWithChildren } from 'react'
import clsx from 'clsx'
import { motion } from 'framer-motion'
import { slideLeftInOut, slideRightInOUt } from '@utils/animations'
import { type CommonProps, type ComponentRenderer } from '@models/commons'
import { handleReactElementOrRenderer } from '@utils/commons'
import CloseButton from '@components/CloseButton'

import styles from './SidePanel.module.scss'

/**
 * SidePanel component description
 */
const SidePanel: FC<SidePanelProps> = (props) => {
  const { active, onClose, position, title, className, children, ActionRenderer, FooterRenderer, ...rest } = props
  const animation = position === 'right' ? slideRightInOUt : slideLeftInOut
  const classList = clsx(styles.slidePanel, active && styles.active, {
    [styles.left]: !position || position === 'left',
    [styles.right]: position === 'right'
  }, className)

  return (
    <motion.aside {...animation} className={classList} {...rest}>
      <header>
        <div className={styles.headerContent}>
          <h2>{title}</h2>
        </div>
        <div className={styles.actions}>
          {ActionRenderer
            ? handleReactElementOrRenderer(ActionRenderer)
            : <CloseButton onClick={onClose} />}
        </div>
      </header>
      <div className={styles.content}>
        {children}
      </div>
      {FooterRenderer && (
        <footer>
          {handleReactElementOrRenderer(FooterRenderer)}
        </footer>
      )}
    </motion.aside>
  )
}

export interface SidePanelProps extends PropsWithChildren<CommonProps> {
  title: string
  active?: boolean
  onClose?: () => void
  position?: 'left' | 'right'
  ActionRenderer?: ComponentRenderer | React.ReactElement
  FooterRenderer?: ComponentRenderer | React.ReactElement
}

export default SidePanel
