import { createElement, isValidElement, type MouseEvent, type ReactElement } from 'react'
import { type ComponentRenderer } from '@models/commons'

let ids = 0
/**
 * Generates a unique id of type number.
 * This function is commonly employed by components that need to generate unique ids for their children.
 */
export const uniqueId = () => {
  ids += 1
  return ids
}

/**
 * Prevents the default behaviour of the event and stops it from propagating to the parent elements.
 *
 * Basic Usage:
 *
 * <button onClick={stopPropagation}>Click Me</button>
 */
export const stopPropagation = <TEvent extends MouseEvent>(event: TEvent) => {
  event.preventDefault()
}

/**
 * Accepts a value that may be either a ReactElement or a ComponentRenderer and ensures that the corresponding
 * React Element instance is returned. This function is commonly employed by components that accept both ReactElements and
 * ComponentRenderers as props to guarantee that they are handled appropriately.
 *
 * Basic Usage:
 *
 * const MyComponent = ({ icon }) => {
 *  const iconElement = handleReactElementOrRenderer(icon)
 *
 *  return (
 *    <div>
 *      {iconElement}
 *    </div>
 *  )
 *  }
 */
export const handleReactElementOrRenderer = (elementOrRenderer?: ReactElement | ComponentRenderer) => {
  if (!elementOrRenderer) return null
  if (isValidElement(elementOrRenderer)) return elementOrRenderer as ReactElement

  return createElement(elementOrRenderer)
}
