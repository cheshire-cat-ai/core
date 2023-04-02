import React, { type FC, type PropsWithChildren } from 'react'
import clsx from 'clsx'
import { AnimatePresence, motion } from 'framer-motion'
import { slideLeftInOut, slideRightInOUt } from '@utils/animations'
import { type CommonProps, type ComponentRenderer } from '@models/commons'
import { handleReactElementOrRenderer } from '@utils/commons'
import CloseButton from '@components/CloseButton'

import styles from './SidePanel.module.scss'
import Spinner from '@components/Spinner'

/**
 * SidePanel component description
 */
const SidePanel: FC<SidePanelProps> = (props) => {
  const { active, onClose, position, title, className, children, ActionRenderer, ...rest } = props
  const animation = position === 'right' ? slideRightInOUt : slideLeftInOut
  const classList = clsx(styles.slidePanel, active && styles.active, {
    [styles.left]: !position || position === 'left',
    [styles.right]: position === 'right'
  }, className)

  return (
    <AnimatePresence>
      <motion.aside {...animation} className={classList} {...rest}>
        <header>
          <div className={styles.headerContent}>
            <h2>{title}</h2>
          </div>
          <div className={styles.actions}>
            {ActionRenderer
              ? handleReactElementOrRenderer(ActionRenderer, { onClose })
              : <CloseButton onClick={onClose} />}
          </div>
        </header>
        <div className={styles.content}>
          {children}
          <Spinner size={20} />
        </div>
      </motion.aside>
    </AnimatePresence>
  )
}

export interface SidePanelProps extends PropsWithChildren<CommonProps> {
  title: string
  active?: boolean
  onClose?: () => void
  position?: 'left' | 'right'
  ActionRenderer?: ComponentRenderer
}

export default SidePanel
