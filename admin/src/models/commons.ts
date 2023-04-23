import { type HTMLAttributes, type JSXElementConstructor } from 'react'

/**
 * Defines a shared interface for specifying the properties that are ubiquitous across all components.
 * This interface serves as a standardized blueprint for defining and validating component props.
 *
 * Basic Usage:
 *
 * export interface MyComponentProps extends CommonProps {
 *  // ... other props
 * }
 */
export interface CommonProps<TElement extends HTMLElement = HTMLElement> {
  readonly className?: HTMLAttributes<TElement>['className']
  readonly style?: HTMLAttributes<TElement>['style']
}

/**
 * Defines a generic component constructor (class or function) that can be used to render a component.
 * The purpose of this type is to help define the props of components that involve other components (allow components
 * injection). ComponentRenderer is a generic type, it allows for the definition of the prop type that the renderer can
 * receive.
 *
 * Basic Usage:
 *
 * export interface MyComponentProps {
 *   HeaderRenderer: ComponentRenderer<{ title: string }>
 * }
 */
export type ComponentRenderer<TProps = Record<string, unknown>> = JSXElementConstructor<TProps> | string

/**
 * A base interface for defining the state of asynchronous operations.
 * This is intended as a base for other interfaces, should not be used directly
 */
export interface AsyncStateBase {
  readonly loading: boolean
  readonly error?: string
}

/**
 * A generic interface for defining the state of an asynchronous operation that returns data (like fetch)
 */
export interface AsyncState<TData> extends AsyncStateBase {
  readonly data?: TData
}

/**
 * Defines a generic interface for defining the state of an asynchronous operation that returns data and can be updated.
 */
export interface UpdatableState<TData> extends AsyncState<TData> {
  readonly updating: boolean
}
