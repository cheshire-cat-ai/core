/**
 * This module defines and export a collection of utility functions that are commonly used throughout the application.
 * The functions are grouped by their purpose and exported as named exports.
 */

import { createElement, isValidElement, type ReactElement } from 'react'
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
 * Accepts a value that may be either a ReactElement or a ComponentRenderer and ensures that the corresponding
 * React Element instance is returned. This function is commonly employed by components that accept both ReactElements
 * and ComponentRenderers as props to guarantee that they are handled appropriately.
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

/**
 * Returns the current timestamp in milliseconds.
 */
export const now = () => new Date().getTime()

/**
 * Renders an empty ReactElement.
 * Basically just a function that returns null lol
 */
export const EmptyReactElement = () => null

/**
 * Returns a promise that contains the response body as a JSON object.
 */
export const toJSON = async <TResult>(response: Response) => await (response.json() as Promise<TResult>)

/**
 * Takes in a string and returns a new string with the first letter capitalized
 */
export const firstLetter = <TString extends string>(str: TString) => str.charAt(0).toUpperCase()
