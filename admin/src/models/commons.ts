/**
 * Defines a generic interface for defining the state of an asynchronous operation.
 */
export interface AsyncStateBase {
  loading: boolean
  error?: string
}

/**
 * Defines a generic interface for defining the state of an asynchronous operation that returns data.
 */
export interface AsyncState<TData> extends AsyncStateBase {
  data?: TData
}

/**
 * TODO: document this
 */
export interface UpdatableState<TData> extends AsyncState<TData> {
  updating: boolean
}
